# GPA Tracker

A mobile-first GPA and grade tracker for university students, built with **Python, KivyMD and SQLite**. It follows the Egerton University grading regulations (Rules and Regulations 2020, section 16.4.1) and runs fully offline on Android.

Each student's marks stay in a private database on their own phone. There is no server and no account.

<!-- Add your screenshots to docs/screenshots/ and uncomment: -->
<!-- <p><img src="docs/screenshots/courses.jpg" width="23%"> <img src="docs/screenshots/summary.jpg" width="23%"> <img src="docs/screenshots/planner.jpg" width="23%"> <img src="docs/screenshots/data.jpg" width="23%"></p> -->

## Features

- **Courses:** add, edit, delete and sort courses, with a live grade preview as you type.
- **Grading:** final mark = coursework 30% + exam 70%, rounded half-up, then mapped to a letter grade and grade points.
- **Summary:** cumulative GPA, per-semester GPA with a progress bar, total credits, quality points, credit-weighted mean mark, and academic standing (including discontinuation risk).
- **Planner:** choose a target class or GPA and the credits left. It works out the average you still need, and says plainly when a target can no longer be reached.
- **Data:** verified backups, CSV export for Excel or Google Sheets, and the grading scale.
- **Self-repair:** if the grading rules change, saved grades are recalculated from the stored marks after a safety backup.

## Project structure

The code is split into four layers. A layer may only use the layers below it.

```
ui  ─────────▶  controllers  ─────────▶  data  ─────────▶  core
Kivy screens    what the app does        SQLite, files     the rules
```

```
gpa-tracker/
├── main.py                     entry point
├── gpatracker/
│   ├── core/                   pure rules, no I/O
│   │   ├── config.py             every grading rule and setting, in one place
│   │   ├── grading.py            final mark, GPA, weighted mean, standing
│   │   ├── planner.py            "what do I need?" maths
│   │   ├── validation.py         typed text -> trusted values
│   │   ├── typing_rules.py       per-key-press input rules
│   │   ├── regrading.py          re-grade saved courses under the current rules
│   │   ├── sorting.py            course ordering
│   │   ├── formatting.py         number formatting
│   │   └── models.py             the Course record
│   ├── data/                   storage
│   │   ├── database.py           the only module that speaks SQL
│   │   ├── errors.py             SQLite errors turned into plain words
│   │   └── exporting.py          dated file names and CSV export
│   ├── controllers/            use-cases: plain text in, plain values out
│   │   ├── courses.py            validate, grade, save, edit, delete, preview
│   │   ├── summary.py            numbers for the Courses and Summary screens
│   │   ├── planning.py           the Planner screen's result
│   │   └── maintenance.py        backup, export, start-up grade repair
│   └── ui/                     KivyMD interface
│       ├── app.py                glue: reads boxes, shows results, dialogs
│       ├── layout.py             all screens, in Kivy's KV language
│       ├── components.py         reusable widgets
│       ├── theme.py              design tokens: colour, spacing, type scale
│       └── crash.py              errors go to crash_log.txt
├── tests/                      222 tests, none needs Kivy
├── docs/screenshots/
├── buildozer.spec              Android build settings
└── .github/workflows/build.yml cloud APK build
```

**Why this shape**
- Grading and planning knowledge lives in `core` and never touches a screen or a file, so it is easy to test and reuse.
- Controllers hold what the app does. The screen hands them plain text and gets a plain result or a clear error back. For example, an invalid exam mark raises an error that names the exam box, and the screen only has to mark that box red.
- `ui` contains no grading or SQL. Swapping the interface, or the storage, touches one layer.
- `tests/test_architecture.py` enforces the rule: a lower layer importing a higher one, or any layer below `ui` importing Kivy, fails the test run.

## Tools and technologies

| Area | Tool | Used for |
|---|---|---|
| Language | Python 3.13 | Everything |
| UI | Kivy 2.3.0 and KivyMD 1.2.0 | Touch-first Android interface, dialogs, menus, icons |
| Layout | Kivy KV language | Declarative screens and component styles |
| Storage | SQLite (`sqlite3`) | Local database with `CHECK` constraints on credits, marks and points |
| Arithmetic | `decimal.Decimal` | No floating-point drift in marks, GPA or planner results |
| Testing | `unittest` | 222 tests for the rules, database, controllers and layering |
| Android on-device | Pydroid 3 | Running and debugging on the phone during development |
| Packaging | Buildozer and GitHub Actions | Building the APK in the cloud |

## Design system

All colours and sizes come from `ui/theme.py`, and the screens are built from a small set of components.

- **Colour:** deep indigo primary, teal accent, soft grey background, white cards. Amber and red are used only for warnings and errors. Grade badges are colour-coded A to F.
- **Type scale:** 44sp GPA, 20sp titles, 18sp key numbers, 16sp codes and inputs, 14sp body, 12sp captions.
- **Spacing:** one screen margin, one card padding, one corner radius, 48dp inputs and buttons.
- **Components:** `Card`, `Collapsible`, `GradeBadge`, `CourseItem`, `SemesterRow`, `ScaleRow`, `Banner`, `EmptyState`, `PlanResult`, `Field`, `DropField`, `SolidButton`, `NavItem`.
- **Navigation and motion:** custom app bar and bottom navigation, and dialogs that fade in and out.

## Bugs encountered and how they were fixed

### Building the KivyMD interface

| Problem | Cause | Fix |
|---|---|---|
| `Unable to find any valuable Window provider` | The script was run from Pydroid's terminal, which has no graphics window | Run from the editor's Run button |
| A fresh empty database could have been used | The first version assumed Android folders were read-only | Use `grades.db` whenever its folder is writable; fall back to private storage only in a packaged APK |
| App closed with no message | `ButtonBehavior` imported from the wrong module | Import from `kivy.uix.behaviors` |
| KV failed to load | Five widgets written without the trailing colon | Added the colons and scripted a check for bare lines |
| `'NoneType' object has no attribute 'get_window_matrix'` | My `Selector` widget shared its name with Kivy's internal text-selection handle | Renamed it `DropField` |
| `'ActionButton' object has no attribute 'filled'` | Same name clash with Kivy's own `ActionButton` | Renamed it `SolidButton` |
| Errors looked like a blank white screen | Error text was white on a light background | Dark text, and every error is also written to `crash_log.txt` |
| Dialogs popped up abruptly | No transition | One shared function fades dialogs in and out |
| Couldn't type a decimal point in credits or marks (e.g. 1.5) | Kivy's `input_type: "number"` opens Android's digits-only keypad, which has no "." key | Number boxes use the normal keyboard; the typing rules still refuse anything that isn't a number, and a decimal comma is read as a point |
| The Planner's "Aim for" menu would not open | The hidden Target GPA box was folded to zero height, but its field kept its size and lay over "Aim for"; Kivy lets a disabled widget swallow taps | A `Collapsible` box that ignores touches while folded |
| A box marked red by a failed save stayed red on the next form | The error flags were only cleared when Save was pressed | Opening the form clears them |
| The APK would crash on its first database call | python-for-android leaves out `sqlite3` unless it is listed | Added `sqlite3` to the Buildozer requirements |

Kivy resolves widget names globally, so custom widgets need names Kivy's own widgets do not use.

### Rules and storage (found by the test suite)

| Problem | Fix |
|---|---|
| Python's default rounding goes to the nearest even digit and could land a mark on the wrong side of a grade boundary | Round half-up with `Decimal`; boundary tests for every grade |
| Matching years with `startswith("Y1")` also caught `Y10`, hiding a failed Year 1 | Match the year exactly; regression test |
| Saving an unchanged edit could shift stored values | Read values back as `Decimal`; a no-change save leaves every value identical |
| Stored grades went stale when the rules changed | Re-grade from the stored marks, after a safety backup |
| Locked, read-only, full or damaged database files surfaced as raw SQLite errors | `errors.py` and a guard in `database.py` turn them into plain-words messages; a damaged file is never deleted or overwritten |
| A backup of a locked database retried forever (found while moving the tests into this structure) | The backup gives up after about two seconds with a clear "busy" message and leaves no partial file |
| A failed backup could leave a file that looked real | Write to a temporary name, verify the copy, and only then give it its final name |

## Running it

```bash
pip install -r requirements.txt
python main.py
```

On Android with Pydroid 3, install `kivy` and `kivymd` from the Pip menu, open `main.py` and press Run.

Run the tests (no Kivy needed):

```bash
python tests/run_tests.py
```

## Building the APK

Push to GitHub, then either run the **Build APK** workflow from the Actions tab or push a version tag:

```bash
git tag v2.1
git push origin v2.1
```

The workflow runs the tests first and only builds if they pass. The APK is attached to the run as a downloadable artifact. The first build takes about 30 minutes; later builds reuse the cached Android SDK.

For each release I:

1. Raise `version` and `android.numeric_version` in `buildozer.spec`, so Android treats it as an update.
2. Run `python tests/run_tests.py`.
3. Tag and push.

Updates must be signed with the same key to keep users' data. The workflow currently builds a debug APK, so it's fine for sideloading but not for the Play Store.

## Privacy

Marks are stored only in the app's own database on the device. Nothing is sent anywhere. `grades.db` is in `.gitignore` so personal data is never published.

## Roadmap

- Restore-from-backup button.
- One fixed release signing key.
- An in-app "new version available" notice.
- Android status-bar and keyboard insets.
- Automated screenshot checks for the Kivy screens.
