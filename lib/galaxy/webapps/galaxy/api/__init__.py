"""
This module *does not* contain API routes. It exclusively contains dependencies to be used in FastAPI routes
"""
import inspect
from typing import (
    Any,
    AsyncGenerator,
    cast,
    Optional,
    Type,
    TypeVar,
)

from fastapi import (
    Cookie,
    Form,
    Header,
    Query,
)
from fastapi.params import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic.main import BaseModel
try:
    from starlette_context import context as request_context
except ImportError:
    request_context = None
from starlette.requests import Request

from galaxy import (
    app as galaxy_app,
    model,
)
from galaxy.exceptions import (
    AdminRequiredException,
    UserCannotRunAsException,
    UserInvalidRunAsException,
)
from galaxy.managers.session import GalaxySessionManager
from galaxy.managers.users import UserManager
from galaxy.model import User
from galaxy.schema.fields import EncodedDatabaseIdField
from galaxy.security.idencoding import IdEncodingHelper
from galaxy.structured_app import StructuredApp
from galaxy.web.framework.decorators import require_admin_message
from galaxy.webapps.base.controller import BaseAPIController
from galaxy.work.context import (
    GalaxyAbstractRequest,
    SessionRequestContext,
)


def get_app() -> StructuredApp:
    return cast(StructuredApp, galaxy_app.app)


async def get_app_with_request_session() -> AsyncGenerator[StructuredApp, None]:
    app = get_app()
    request_id = request_context.data['X-Request-ID']
    app.model.set_request_id(request_id)
    try:
        yield app
    finally:
        app.model.unset_request_id(request_id)


DependsOnApp = Depends(get_app_with_request_session)


T = TypeVar("T")


class GalaxyTypeDepends(Depends):
    """Variant of fastapi Depends that can also work on WSGI Galaxy controllers."""

    def __init__(self, callable, dep_type):
        super().__init__(callable)
        self.galaxy_type_depends = dep_type


def depends(dep_type: Type[T]) -> Any:

    def _do_resolve(request: Request):
        return get_app().resolve(dep_type)

    return GalaxyTypeDepends(_do_resolve, dep_type)


def get_session_manager(app: StructuredApp = DependsOnApp) -> GalaxySessionManager:
    # TODO: find out how to adapt dependency for Galaxy/Report/TS
    return GalaxySessionManager(app.model)


def get_session(session_manager: GalaxySessionManager = Depends(get_session_manager),
                security: IdEncodingHelper = depends(IdEncodingHelper),
                galaxysession: Optional[str] = Cookie(None)) -> Optional[model.GalaxySession]:
    if galaxysession:
        session_key = security.decode_guid(galaxysession)
        if session_key:
            return session_manager.get_session_from_session_key(session_key)
        # TODO: What should we do if there is no session? Since this is the API, maybe nothing is the right choice?
    return None


def get_api_user(
        security: IdEncodingHelper = depends(IdEncodingHelper),
        user_manager: UserManager = depends(UserManager),
        key: Optional[str] = Query(None),
        x_api_key: Optional[str] = Header(None),
        run_as: Optional[EncodedDatabaseIdField] = Header(
            default=None,
            title='Run as User',
            description=(
                'The user ID that will be used to effectively make this API call. '
                'Only admins and designated users can make API calls on behalf of other users.'
            )
        )
) -> Optional[User]:
    api_key = key or x_api_key
    if not api_key:
        return None
    user = user_manager.by_api_key(api_key=api_key)
    if run_as:
        if user_manager.user_can_do_run_as(user):
            try:
                decoded_run_as_id = security.decode_id(run_as)
            except Exception:
                raise UserInvalidRunAsException
            return user_manager.by_id(decoded_run_as_id)
        else:
            raise UserCannotRunAsException
    return user


def get_user(galaxy_session: Optional[model.GalaxySession] = Depends(get_session), api_user: Optional[User] = Depends(get_api_user)) -> Optional[User]:
    if galaxy_session:
        return galaxy_session.user
    return api_user


class UrlBuilder:

    def __init__(self, request: Request):
        self.request = request

    def __call__(self, name: str, **path_params):
        qualified = path_params.pop("qualified", False)
        if qualified:
            return self.request.url_for(name, **path_params)
        return self.request.app.url_path_for(name, **path_params)


class GalaxyASGIRequest(GalaxyAbstractRequest):
    """Wrapper around Starlette/FastAPI Request object.

    Implements the GalaxyAbstractRequest interface to provide access to some properties
    of the request commonly used."""

    def __init__(self, request: Request):
        self.__request = request

    @property
    def base(self) -> str:
        return str(self.__request.base_url)

    @property
    def host(self) -> str:
        return str(self.__request.client.host)


DependsOnUser = Depends(get_user)


def get_current_history_from_session(galaxy_session: Optional[model.GalaxySession]) -> Optional[model.History]:
    if galaxy_session:
        return galaxy_session.current_history
    return None


def get_trans(request: Request, app: StructuredApp = DependsOnApp, user: Optional[User] = Depends(get_user),
              galaxy_session: Optional[model.GalaxySession] = Depends(get_session),
              ) -> SessionRequestContext:
    url_builder = UrlBuilder(request)
    galaxy_request = GalaxyASGIRequest(request)
    return SessionRequestContext(
        app=app, user=user,
        galaxy_session=galaxy_session,
        url_builder=url_builder,
        request=galaxy_request,
        history=get_current_history_from_session(galaxy_session),
    )


DependsOnTrans = Depends(get_trans)


def get_admin_user(trans: SessionRequestContext = DependsOnTrans):
    if not trans.user_is_admin:
        raise AdminRequiredException(require_admin_message(trans.app.config, trans.user))
    return trans.user


AdminUserRequired = Depends(get_admin_user)


class BaseGalaxyAPIController(BaseAPIController):

    def __init__(self, app: StructuredApp):
        super().__init__(app)


class Router(InferringRouter):
    """A FastAPI Inferring Router tailored to Galaxy.
    """

    def get(self, *args, **kwd):
        """Extend FastAPI.get to accept a require_admin Galaxy flag."""
        return super().get(*args, **self._handle_galaxy_kwd(kwd))

    def put(self, *args, **kwd):
        """Extend FastAPI.put to accept a require_admin Galaxy flag."""
        return super().put(*args, **self._handle_galaxy_kwd(kwd))

    def post(self, *args, **kwd):
        """Extend FastAPI.post to accept a require_admin Galaxy flag."""
        return super().post(*args, **self._handle_galaxy_kwd(kwd))

    def delete(self, *args, **kwd):
        """Extend FastAPI.delete to accept a require_admin Galaxy flag."""
        return super().delete(*args, **self._handle_galaxy_kwd(kwd))

    def _handle_galaxy_kwd(self, kwd):
        require_admin = kwd.pop("require_admin", False)
        if require_admin:
            if "dependencies" in kwd:
                kwd["dependencies"].append(AdminUserRequired)
            else:
                kwd["dependencies"] = [AdminUserRequired]
        return kwd

    @property
    def cbv(self):
        """Short-hand for frequently used Galaxy-pattern of FastAPI class based views.

        Creates a class-based view for for this router, for more information see:
        https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/
        """
        return cbv(self)


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints.

    See https://github.com/tiangolo/fastapi/issues/2387#issuecomment-731662551
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig    # type: ignore
    cls.as_form = _as_form          # type: ignore
    return cls


async def try_get_request_body_as_json(request: Request) -> Optional[Any]:
    """Returns the request body as a JSON object if the content type is JSON."""
    if "application/json" in request.headers.get("content-type", ""):
        body = await request.json()
        return body
    return None
