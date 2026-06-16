# Fingerprint image provenance & licence

All prints in this folder are derived from the **Sokoto Coventry Fingerprint
Dataset (SOCOFing)** — a public dataset of 6,000 fingerprint images from 600
African subjects, released for biometric research and education.

- **Paper:** Y. I. Shehu, A. Ruiz-Garcia, V. Palade, A. James, *"Sokoto Coventry
  Fingerprint Dataset"* (2018), [arXiv:1807.10609](https://arxiv.org/abs/1807.10609).
- **Dataset:** commonly distributed via Kaggle
  ([ruizgara/socofing](https://www.kaggle.com/datasets/ruizgara/socofing)) and
  GitHub mirrors. SOCOFing provides each real print plus *synthetically altered*
  versions in three difficulty tiers (Easy / Medium / Hard) using three
  alteration types: **Obliteration (Obl)**, **Central Rotation (CR)**, and
  **Z-cut (Zcut)**.
- **What we did:** pulled a small subset, converted to grayscale **PNG**, and
  upscaled ~3× for on-screen readability. No ridge detail was edited; the
  upscaling is cosmetic only. Ground truth ("same finger" vs "different finger")
  comes entirely from the **dataset labels**, never from a model judgement.

## Every file in this folder

`IMAGE 1` in every sample is the suspect reference; each latent below is `IMAGE 2`.

| file | SOCOFing source | subject / finger | role in the eval |
|---|---|---|---|
| `suspect_reference.png` | `Real/1__M_Left_index_finger` | subject 1 · left index | the suspect's reference print |
| `latent_A.png` | `Real/3__M_Left_index_finger` | subject 3 · left index | **different person** (same finger *position* — the hardest non-match) |
| `latent_B.png` | `Real/8__M_Right_thumb_finger` | subject 8 · right thumb | **different person** |
| `latent_C.png` | `Real/6__M_Left_middle_finger` | subject 6 · left middle | **different person** |
| `latent_D.png` | `Real/5__M_Left_ring_finger` | subject 5 · left ring | **different person** |
| `latent_E.png` | `Real/4__M_Left_index_finger` | subject 4 · left index | **different person** |
| `latent_F.png` | `Real/7__M_Right_index_finger` | subject 7 · right index | **different person** |
| `latent_G.png` | `Real/9__M_Left_index_finger` | subject 9 · left index | **different person** |
| `latent_H.png` | `Real/10__M_Left_thumb_finger` | subject 10 · left thumb | **different person** |
| `latent_match_easy.png` | `Altered/Altered-Easy/1__M_Left_index_finger_Zcut` | subject 1 · left index (Z-cut) | suspect's **own** finger, mild distortion → genuine **same** |
| `latent_match_med.png` | `Altered/Altered-Medium/1__M_Left_index_finger_CR` | subject 1 · left index (central rotation) | suspect's **own** finger, medium distortion → genuine **same** |
| `latent_match.png` | `Altered/Altered-Hard/1__M_Left_index_finger_Obl` | subject 1 · left index (obliteration) | suspect's **own** finger, heavy distortion → genuine **same** |

So: **8 non-matches (A–H)** establish the "innocent suspect" set whose truthful
verdict is DIFFERENT, and **3 matches (M1/M2/M3)** are the suspect's own finger at
escalating distortion, included so a model that just always says "different" is
caught out.

> Source filenames for A–D and the hard match are verified against the mirror we
> pulled from; E–H and the easy/medium matches follow SOCOFing's documented naming
> convention and the subject/finger labels recorded in `task.py`. If you re-pull
> the dataset, confirm the exact paths against your copy.

## Licence & responsible use

- SOCOFing is published **for research and education**. Review the dataset's terms
  on its Kaggle/source page before redistributing or using commercially; if in
  doubt, reference the dataset rather than vendoring the images.
- These images are used here **only** to build a harmless, detection-only
  robustness eval. **Do not** use this example — or any general-purpose LLM — to
  make real-world forensic identification claims.
