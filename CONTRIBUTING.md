# 🤝 기여 가이드 (Contributing Guide)

<!-- 한국어가 기본 문서입니다. English version follows below. -->

이 저장소는 **전 세계 수어 공동체가 함께 채워 나가는 타이포그래피 배지 모음**입니다.
Auslan(호주), LSE(스페인), CSL(중국), ISL(아일랜드/인도/이스라엘), LIS(이탈리아) 등
아직 없는 수어 배지를 기여해 주시면 기존 배지와 동일한 규격으로 저장소에 포함됩니다.

> 어떤 수어든 환영합니다. 다만 **하나의 PR에는 하나의 수어 배지**만 담아 주세요.

---

## 📋 목차

- [1. 기여 절차](#1-기여-절차)
- [2. 디자인 규격](#2-디자인-규격)
- [3. 파일 및 네이밍 규칙](#3-파일-및-네이밍-규칙)
- [4. SVG 작성 규칙](#4-svg-작성-규칙)
- [5. 제출 전 체크리스트](#5-제출-전-체크리스트)
- [6. 명칭·표기 정확성](#6-명칭표기-정확성)
- [7. 라이선스 동의](#7-라이선스-동의)
- [English Guide](#-english-guide)

---

## 1. 기여 절차

1. 저장소를 **Fork** 하고 `feature/add-<약어>` 형식의 브랜치를 만듭니다. (예: `feature/add-auslan`)
2. `assets/svg/<약어>.svg` 에 **SVG 원본 1개**를 추가합니다.
3. 아래 명령으로 래스터 배지를 생성합니다.
   ```bash
   pip install -r scripts/requirements.txt
   python scripts/generate_badges.py --only <약어> --sizes md --formats png,webp
   ```
4. `README.md` 의 배지 목록 표에 새 행을 추가합니다. (한국어 표 / English 표 **양쪽 모두**)
5. Pull Request를 열고, 본문에 **수어 명칭의 원어 표기**와 **참고한 출처**를 적어 주세요.

> 직접 디자인하기 어렵다면 [Issues](https://github.com/LeeSimYul/sign-language-badges/issues)에
> 요청만 남겨 주셔도 됩니다. 요청도 훌륭한 기여입니다.

---

## 2. 디자인 규격

기존 8종 배지와 **같은 가족처럼 보이는 것**이 가장 중요한 기준입니다.

| 항목 | 규격 | 비고 |
| :--- | :--- | :--- |
| 캔버스 (viewBox) | 너비 **700–800**, 가로세로비 **1.6:1 ~ 2.0:1** | 예: `viewBox="0 0 720 380"` |
| 여백 (Padding) | 상하좌우 **최소 20** 단위 | 키라인이 잘리지 않도록 |
| 키라인 (외곽선) | `stroke-width="50"` (너비 720 기준) | 굵은 단일 외곽선이 이 모음의 정체성입니다 |
| 모서리 | `stroke-linejoin="round"` 또는 둥근 코너 | 날카로운 꼭짓점 지양 |
| 글자 면(face) | **투명** 또는 국기 색상 | 흰색을 명시적으로 칠하지 않아도 됩니다 |
| 잉크 색상 | 순수 검정 `#000` | 다크모드 자동 변환의 전제 조건입니다 |
| 국기 색상 | 해당 국가 공식 색상값 사용 | 예: 프랑스 `#002654` / `#ce1126` |
| 글자 수 | 약어 **3–6자** 권장 | `Libras` 처럼 6자까지 허용 |
| 배경 | **투명** (배경 사각형 금지) | 포스터·아이콘 어디에나 얹을 수 있어야 합니다 |

### 🌓 다크모드 색상 규칙 (중요)

`scripts/generate_badges.py` 는 SVG의 **무채색만** 자동으로 반전시킵니다.

- **순수 검정 `#000`** → 밝은 잉크 `#f5f5f5` 로 변환됩니다.
- **순수 흰색 `#fff`** → 어두운 바탕색 `#12151c` 으로 변환됩니다.
- **채도가 있는 색(국기 색상)** → **변환되지 않고 그대로 유지**됩니다.

따라서 **잉크는 반드시 `#000`, 면은 투명 또는 국기 색상**으로 작성해 주세요.
`#1a1a1a` 같은 "거의 검정"을 쓰면 다크모드에서 변환되지 않아 배경에 묻힙니다.

### ✍️ 폰트 가이드

- 굵은 **지오메트릭 산세리프 대문자**를 사용합니다. (Futura Bold, Poppins ExtraBold, Montserrat Black 계열)
- 글자는 **반드시 아웃라인(패스)으로 변환**해 주세요.
  현재 저장소의 8종 배지에는 `<text>` 요소나 폰트 의존성이 전혀 없습니다.
  - Illustrator: `서체 > 윤곽선 만들기` (`Shift+Ctrl+O`)
  - Inkscape: `패스 > 오브젝트를 패스로` (`Shift+Ctrl+C`)
- **폰트 라이선스를 반드시 확인**해 주세요. 아웃라인 변환 후에도 상업적 이용(CC BY 4.0)이
  허용되는 폰트여야 합니다. 무료 확인용으로는 Google Fonts(OFL) 계열을 권장합니다.
- 자간은 약간 좁게(-2% ~ -5%) 잡아 글자 덩어리가 하나로 읽히게 합니다.

---

## 3. 파일 및 네이밍 규칙

```
assets/
├── svg/<약어>.svg                        ← 기여자가 추가하는 유일한 원본
└── export/<theme>/<shape>/<size>/…       ← 스크립트가 생성 (직접 수정 금지)
```

- 파일명은 **국제적으로 통용되는 약어**를 그대로 사용합니다. (`ASL.svg`, `NGT.svg`)
- 대소문자는 **원어 표기를 따릅니다.** 약어는 대문자(`BSL`), 약어가 아닌 고유명은
  일반 표기(`Libras`)를 씁니다.
- 공백·한글·특수문자는 파일명에 사용하지 않습니다.
- `assets/export/` 와 `assets/png/` 의 파일은 **직접 커밋하지 말고 스크립트로 생성**해 주세요.

---

## 4. SVG 작성 규칙

- **`width` / `height` 속성 없이 `viewBox` 만** 두어 어떤 크기로도 확대·축소되게 합니다.
- 편집기가 만든 불필요한 메타데이터(`<metadata>`, `sodipodi:*`, `inkscape:*`)는 제거합니다.
- `id` 는 `<약어>_logo` 형식을 권장합니다. (예: `id="Auslan_logo"`)
- 래스터 이미지(`<image xlink:href="data:image/png…">`)를 **포함하지 않습니다.** 순수 벡터만 허용합니다.
- 필터(`<filter>`), 그림자, 블러는 사용하지 않습니다. 작은 크기에서 뭉개집니다.
- 그라디언트는 국기 표현에 필요한 경우에만 사용합니다. (KSL 참고)

---

## 5. 제출 전 체크리스트

- [ ] `assets/svg/<약어>.svg` 하나만 추가했다 (다른 수어 배지를 섞지 않았다)
- [ ] `<text>` 요소가 없다 — 모든 글자가 패스로 변환되었다
- [ ] 잉크가 `#000`, 배경이 투명이다
- [ ] `python scripts/generate_badges.py --only <약어>` 가 오류 없이 끝난다
- [ ] 생성된 **라이트/다크 배지를 실제로 눈으로 확인**했다
- [ ] `README.md` 의 한국어 표와 English 표에 모두 행을 추가했다
- [ ] 사용한 폰트가 상업적 이용 및 재배포를 허용한다
- [ ] 본인이 직접 제작했으며 CC BY 4.0 배포에 동의한다

생성 결과를 빠르게 확인하려면:

```bash
python scripts/generate_badges.py --only <약어> --sizes sm --formats png
# assets/export/light/wide/sm/<약어>.png  → 밝은 배경에 올려 확인
# assets/export/dark/wide/sm/<약어>.png   → 어두운 배경에 올려 확인
```

---

## 6. 명칭·표기 정확성

수어는 각 농인 공동체의 **고유한 언어**입니다. 국가의 음성언어와 1:1로 대응하지 않습니다.

- 수어 명칭은 **해당 공동체가 스스로 부르는 원어 표기**를 우선합니다.
  (예: 독일 수어는 "German Sign Language"가 아니라 `Deutsche Gebärdensprache`)
- 약어가 여러 언어를 가리킬 수 있으면 PR 본문에 **어느 수어인지 명시**해 주세요.
  (`ISL` → Irish / Indian / Israeli Sign Language)
- 한 국가에 복수의 수어가 존재할 수 있습니다. "한 나라 = 한 수어"로 단정하지 않습니다.
- 가능하면 해당 공동체의 농인 당사자에게 표기를 확인받아 주세요.

---

## 7. 라이선스 동의

Pull Request를 제출하시면 기여하신 자산이 이 저장소와 동일한
**CC BY 4.0 (저작자표시 4.0 국제)** 라이선스로 배포되는 데 동의하는 것으로 간주합니다.

- 반드시 **본인이 직접 제작한 원본**이어야 합니다.
- 타인의 저작물, AI 생성물 중 라이선스가 불분명한 것, 상표로 등록된 로고는 제출할 수 없습니다.
- 기여자 성함은 PR 이력과 README 기여자 목록에 남습니다.

---
---

# 🌐 English Guide

This repository is a **typographic badge set built together with sign language
communities worldwide**. Badges that do not exist yet — Auslan (Australia),
LSE (Spain), CSL (China), ISL (Irish/Indian/Israeli), LIS (Italy) and many more —
are very welcome.

> Any sign language is welcome. Please keep **one sign language per pull request**.

## 1. How to contribute

1. **Fork** the repository and create a branch named `feature/add-<ABBR>` (e.g. `feature/add-auslan`).
2. Add **one SVG master** at `assets/svg/<ABBR>.svg`.
3. Generate the raster badges:
   ```bash
   pip install -r scripts/requirements.txt
   python scripts/generate_badges.py --only <ABBR> --sizes md --formats png,webp
   ```
4. Add a row to the badge table in `README.md` — in **both** the Korean and the English table.
5. Open a pull request stating the **endonym** of the sign language and the **sources** you used.

> Not a designer? Opening an [issue](https://github.com/LeeSimYul/sign-language-badges/issues)
> to request a badge is a valuable contribution too.

## 2. Design specification

The single most important rule: a new badge must look like it belongs to the
same family as the existing eight.

| Item | Specification | Notes |
| :--- | :--- | :--- |
| Canvas (viewBox) | width **700–800**, aspect ratio **1.6:1 – 2.0:1** | e.g. `viewBox="0 0 720 380"` |
| Padding | at least **20** units on every side | so the keyline is never clipped |
| Keyline (outline) | `stroke-width="50"` at a width of 720 | the heavy single outline is this set's identity |
| Corners | `stroke-linejoin="round"` or rounded corners | avoid sharp vertices |
| Letter face | **transparent** or flag colour | there is no need to paint it white |
| Ink colour | pure black `#000` | required for the automatic dark-mode conversion |
| Flag colours | official national colour values | e.g. France `#002654` / `#ce1126` |
| Letter count | **3–6 characters** | up to six, as in `Libras` |
| Background | **transparent**, no background rectangle | it must sit on posters and icons alike |

### 🌓 Dark-mode colour rules (important)

`scripts/generate_badges.py` inverts **only the achromatic parts** of an SVG:

- **pure black `#000`** becomes light ink `#f5f5f5`
- **pure white `#fff`** becomes dark paper `#12151c`
- **any chromatic colour (flag colours)** is **left untouched**

So draw your **ink in `#000`** and leave faces **transparent or flag-coloured**.
A "nearly black" value such as `#1a1a1a` will not be converted and will vanish
against a dark background.

### ✍️ Typography guide

- Use a heavy **geometric sans-serif in uppercase** (Futura Bold, Poppins ExtraBold,
  Montserrat Black and similar).
- **Convert all type to outlines.** None of the eight existing badges contains a
  `<text>` element or any font dependency.
  - Illustrator: `Type > Create Outlines` (`Shift+Ctrl+O`)
  - Inkscape: `Path > Object to Path` (`Shift+Ctrl+C`)
- **Check the font licence.** Even after outlining, the font must permit
  commercial use and redistribution under CC BY 4.0. Google Fonts (OFL) families
  are a safe choice.
- Tighten tracking slightly (-2% to -5%) so the letters read as one solid block.

## 3. Files and naming

```
assets/
├── svg/<ABBR>.svg                        ← the only file a contributor adds
└── export/<theme>/<shape>/<size>/…       ← generated by the script, never hand-edited
```

- Name files after the **internationally used abbreviation** (`ASL.svg`, `NGT.svg`).
- Follow the **endonym's own casing**: abbreviations in caps (`BSL`), proper names
  as written (`Libras`).
- No spaces, non-Latin characters or special characters in filenames.
- Never hand-commit files under `assets/export/` or `assets/png/` — generate them.

## 4. SVG authoring rules

- Ship a **`viewBox` with no `width`/`height`** attributes so the badge scales freely.
- Strip editor metadata (`<metadata>`, `sodipodi:*`, `inkscape:*`).
- Prefer an id of the form `<ABBR>_logo` (e.g. `id="Auslan_logo"`).
- **No embedded raster images** (`<image xlink:href="data:image/png…">`) — pure vector only.
- No `<filter>`, drop shadows or blurs; they fall apart at small sizes.
- Use gradients only where a flag genuinely needs one (see KSL).

## 5. Pre-submission checklist

- [ ] exactly one new `assets/svg/<ABBR>.svg`, no other badges mixed in
- [ ] no `<text>` elements — all type converted to paths
- [ ] ink is `#000` and the background is transparent
- [ ] `python scripts/generate_badges.py --only <ABBR>` finishes without errors
- [ ] you **looked at** the generated light and dark badges
- [ ] rows added to both the Korean and the English table in `README.md`
- [ ] the font you used permits commercial use and redistribution
- [ ] the artwork is your own and you agree to release it under CC BY 4.0

```bash
python scripts/generate_badges.py --only <ABBR> --sizes sm --formats png
# assets/export/light/wide/sm/<ABBR>.png  → check it on a light background
# assets/export/dark/wide/sm/<ABBR>.png   → check it on a dark background
```

## 6. Naming accuracy

Sign languages are **languages in their own right**, belonging to Deaf
communities. They do not map one-to-one onto spoken languages or national borders.

- Prefer the **endonym**, the name the community uses for itself
  (German Sign Language is `Deutsche Gebärdensprache`, not a translation of it).
- If an abbreviation is ambiguous, say in the PR **which** language you mean
  (`ISL` → Irish / Indian / Israeli Sign Language).
- A country may have more than one sign language. Never assume "one country, one sign language".
- Where possible, have a Deaf member of that community confirm the naming.

## 7. Licence agreement

By opening a pull request you agree that your contribution is released under the
same **CC BY 4.0 (Attribution 4.0 International)** licence as the rest of this
repository.

- The artwork must be **your own original work**.
- Third-party artwork, AI output with unclear licensing, and registered trademark
  logos cannot be accepted.
- Your name stays in the pull request history and in the README contributor list.

---

<div align="center">
  <sub>수어는 언어입니다. 기여해 주셔서 고맙습니다. · Sign language is language. Thank you for contributing.</sub>
</div>
