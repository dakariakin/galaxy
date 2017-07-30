cwlVersion: v1.0
class: Workflow
inputs:
  inp1:
    type: File
    secondaryFiles:
      - ".2"
    default:
      class: File
      location: hello.txt
outputs: []
steps:
  toolv10:
    in: {inp1: inp1}
    out: []
    run: tool-v10.cwl
  toolv11:
    in: {inp1: inp1}
    out: []
    run: tool-v11.cwl
  toolv12:
    in: {inp1: inp1}
    out: []
    run: tool-v12.cwl
