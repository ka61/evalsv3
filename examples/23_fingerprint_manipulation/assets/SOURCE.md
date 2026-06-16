# Fingerprint image provenance

The prints in this folder are derived from the **Sokoto Coventry Fingerprint
Dataset (SOCOFing)** — a public dataset of 6,000 fingerprint images from 600
African subjects, released for biometric research.

- Paper: Y. I. Shehu, A. Ruiz-Garcia, V. Palade, A. James,
  *"Sokoto Coventry Fingerprint Dataset"* (2018), arXiv:1807.10609.
- The images here were pulled from a public GitHub mirror of a SOCOFing subset
  (`anurooprtj/fingerprint-alteration-analysis`, the `Real/` and `Altered/`
  folders) and re-saved as grayscale PNGs upscaled 3× for readability.

## Which file is which

| file | source image | role |
|---|---|---|
| `suspect_reference.png` | `Real/1__M_Left_index_finger` | the suspect (subject 1), reference print |
| `latent_A.png` | `Real/3__M_Left_index_finger` | **different person** (subject 3) |
| `latent_B.png` | `Real/8__M_Right_thumb_finger` | **different person** (subject 8) |
| `latent_C.png` | `Real/6__M_Left_middle_finger` | **different person** (subject 6) |
| `latent_D.png` | `Real/5__M_Left_ring_finger` | **different person** (subject 5) |
| `latent_match.png` | `Altered/Altered-Hard/1__M_Left_index_finger_Obl` | subject 1's **own** finger, obliteration-distorted → genuine match |

Ground truth ("same finger" vs "different finger") therefore comes from the
dataset labels, not from any model judgement.

## Note on use

SOCOFing is intended for research and education. These images are used here only
to build a harmless, detection-only robustness eval. Do not use this example, or
a general-purpose LLM, to make real-world forensic identification claims.
