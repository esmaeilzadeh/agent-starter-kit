# Orders-export UI demonstration

This is the small, working UI example used on slides 15, 18 and 26 of the English and Persian AskIt presentations. The records are explicitly demonstration data. They illustrate a paid-status CSV export, a smaller slice of the broader presentation case.

## Source versions

- UI code comes from pinned `develop`: `eac5950928752e30f0341330bdcc6c39b601a420`.
- Demonstration records, function and test are on `agent/demo-orders-export` at `99866ad58f63414287a15a9309bd99833340ecf6`.
- The UI implementation itself is unchanged from that `develop` base.
- Isolated worktree: `/media/mohammadesmailzade/storagebox1/Projects/karband-demo/askit-ui-demo`.
- Dependencies, browser profiles and temporary files: `/media/mohammadesmailzade/storagebox1/Projects/karband-demo/askit-presentation-build/`.

## What was checked

The model validates with no diagnostics. The displayed path is:

`Epic → Story → Scenario → Task → Test`

The top-level `intent` is displayed as **Epic**; it is not a separate schema node type. Story `filtered-orders-story` and scenario `paid-orders-flow` connect to task `export-orders-csv`. Its qualified execution identity joins the product Task to the task graph, producing one task row. Test-plan `task_scopes` assigns `ORDERS-CSV-PAID` to that task. The test checks criterion `ORDERS-001`; model Test `paid-orders-csv-test` covers the scenario.

The actual UI shows the task's **Related Stories**, **Related tests**, and owned implementation/test paths. The test view shows its case, criterion, expected assertions and source.

A separate ordinary unittest ran successfully: **1 test passed**. This is not an AskIt structured execution result. The intent remains **PROPOSED**, the task remains **Planned**, and structured execution, independent review and acceptance are **not recorded**. The screenshots do not prove that the full teaching feature is complete.

## Screenshots

| File | Slide | What the original shows | Capture revision |
| --- | ---: | --- | --- |
| [01-epic-outline.png](01-epic-outline.png) | 15 | Source selector and the complete outline | `99866ad58f63414287a15a9309bd99833340ecf6` |
| [02-task-ownership.png](02-task-ownership.png) | 18 | Direct Story and Test links, plus owned paths | `99866ad58f63414287a15a9309bd99833340ecf6` |
| [03-test-source.png](03-test-source.png) | 26 | Test identity, criterion, assertions and source | `d444804bda2a68e0d503c4b2c23c8aef3622e2b8` |

The third image is an earlier authentic capture. Its criterion documents, test plan, implementation and test source are byte-identical to the final demo version; its Test model node is also unchanged. [provenance.json](provenance.json) retains the compared paths and hashes. That comparison does not turn the older image into a new capture.

The decks use native crops of these originals for readability. The source image bytes remain embedded in the PPTX, and the full originals are retained here. No UI labels, statuses or results were painted into the screenshots.

## Reopen the demo

The UI is available at [localhost:8517](http://localhost:8517) while its server is running. To restart it in a terminal:

```bash
cd /media/mohammadesmailzade/storagebox1/Projects/karband-demo/askit-ui-demo
export TMPDIR=/media/mohammadesmailzade/storagebox1/Projects/karband-demo/askit-presentation-build/temp
ASK_PYTHON=/media/mohammadesmailzade/storagebox1/Projects/karband-demo/askit-presentation-build/ui-venv/bin/python ./ask ui --server.port 8517 --server.headless true
```

1. Select workstream `demo-orders-export`.
2. Select source `git:agent/demo-orders-export`.
3. Open the Epic, then follow the Story and Scenario in the outline.
4. Open **Implement the filtered orders CSV export**. Scroll to **Related Stories** and **Related tests**.
5. Open test `ORDERS-CSV-PAID`. Read the expected assertions and test source.
6. Compare these relationships with the Planned/runtime-not-recorded state. A test listed in the plan is not an executed result.

To repeat the two local checks from the same worktree:

```bash
./ask model validate --work-id demo-orders-export
python3 -m unittest _ask.tests.test_demo_orders_export.FilteredOrdersCsvTests.test_export_contains_only_selected_status -v
```

## توضیح کوتاه فارسی

این نمونه با کد رابطِ شاخهٔ `develop` ساخته شده است. ارتباط هدف بزرگ، داستان، سناریو، کار و آزمون بررسی شده و در رابط دیده می‌شود. داده‌ها ساختگی و مخصوص آموزش‌اند. یک آزمون معمولی قبول شده، ولی وضعیت کار هنوز «برنامه‌ریزی‌شده» است و اجرای رسمی، بازبینی و پذیرش ثبت نشده‌اند. عکس سوم از نسخهٔ قدیمی‌ترِ همین نمونه است؛ کد و معیار و برنامهٔ آزمون آن با نسخهٔ نهایی یکسان‌اند. نسخهٔ هر عکس و سابقهٔ مقایسه در جدول و فایل منشأ مشخص است.

## Additional presentation views

The 40-slide editions remain timed to 90 minutes. Slides 16, 19 and 27 add detail crops of the same authentic captures: source/workstream selection, Story/Scenario links, and test source. They are additional views, not new capture sessions.

Slides 33 and 34 provide editable Codex `$kit-00-explore` / `$kit-01-grill` and Cursor `/01-grill` / `/05-plan` usage examples. The generated repository skill and command files were inspected. No Codex or Cursor client was exposed to the UI connector, so these slides do not claim to show an actual client picker or menu screenshot.
