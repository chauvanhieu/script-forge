# Objective checks

Written by auto gates and QC handling. One line per check:
`- K### [scope] check.  hits: N · <slug>/<id>`; scope is script, image, audio or captions, optionally `· <lang>`.
Bump `hits` (and the slug/id) when a check catches a defect again. At most 30 per scope.

- K001 [image] Night and moon scenes: state the exact count in the prompt ("exactly one round full moon, no crescent").  hits: 1 · den-ong-sao/S05
- K002 [image] Plate prompts named "face" must say "head-and-shoulders portrait, face fills the frame"; otherwise the model draws a full body.  hits: 1 · den-ong-sao/C01_face
- K003 [audio · vi] VoiceStudio's Vietnamese word aligner is untrusted; sf_align falls back to pause-anchored approx timings, so put punctuation where the voice should pause.  hits: 16 · den-ong-sao/L001
- K004 [script · vi] Budget Vietnamese lines with the measured speaking rate in library/calibration.json; the untuned estimate overshot 60 s by 7 %.  hits: 1 · den-ong-sao/L016
