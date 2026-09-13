#!/usr/bin/env python3
"""Build a portable 16:9 PPTX of the kit method-and-tooling talk."""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import nsmap
from pptx.oxml import parse_xml
from pptx.util import Emu, Inches, Pt

from pathlib import Path
OUT = str(Path(__file__).resolve().parent / "method-and-tooling.pptx")

BG = RGBColor(0x12, 0x14, 0x1A)
FG = RGBColor(0xEF, 0xE8, 0xD8)
MUTED = RGBColor(0x9B, 0x95, 0x88)
ACCENT = RGBColor(0xC9, 0x86, 0x3A)
PANEL = RGBColor(0x1A, 0x1D, 0x25)

W = Inches(13.333)
H = Inches(7.5)


def _set_run(run, text, size=20, bold=False, color=FG, name="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def fill_slide(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_box(slide, l, t, w, h, color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shape.line.fill.background()
    if color is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
    return shape


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def kicker_title(slide, kicker, title, title_size=32):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(0.35), Inches(12), Inches(0.4))
    p = box.text_frame.paragraphs[0]
    _set_run(p.add_run() if p.runs else p.runs[0] if False else p.add_run(), "", 14, False, ACCENT)
    # first paragraph is empty until we set it
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, kicker.upper(), 13, True, ACCENT)
    tbox = slide.shapes.add_textbox(Inches(0.7), Inches(0.75), Inches(12), Inches(1.4))
    tf = tbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, title, title_size, True, FG)


def body_box(slide, top=2.3, height=4.6):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(top), Inches(12), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    return tf


def add_para(tf, text, size=20, bold=False, color=FG, space=8, first=False):
    p = tf.paragraphs[0] if first and not tf.paragraphs[0].text else tf.add_paragraph()
    if first and not tf.paragraphs[0].runs:
        p = tf.paragraphs[0]
    p.space_after = Pt(space)
    r = p.add_run()
    _set_run(r, text, size, bold, color)
    return p


def add_bullet(tf, text, size=20):
    p = tf.add_paragraph()
    p.level = 0
    p.space_after = Pt(6)
    r = p.add_run()
    _set_run(r, text, size, False, FG)


def add_table(slide, rows, left=0.7, top=2.3, width=12.0, height=4.2, col_w=None):
    n_rows = len(rows)
    n_cols = len(rows[0])
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table
    if col_w:
        for i, w in enumerate(col_w):
            table.columns[i].width = Inches(w)
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            header = i == 0
            _set_run(r, cell_text, 14 if not header else 13, header, MUTED if header else FG)
            # cell fill
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            solid = parse_xml(
                '<a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                f'<a:srgbClr val="{"1A1D25" if header else "12141A"}"/>'
                "</a:solidFill>"
            )
            # remove existing solidFill
            for child in list(tcPr):
                if child.tag.endswith("solidFill"):
                    tcPr.remove(child)
            tcPr.append(solid)
    return table


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    fill_slide(slide)
    return slide


def main():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    # 1 title
    s = new_slide(prs)
    tf = body_box(s, 3.4, 3)
    add_para(tf, "90 MINUTES  ·  AI TEAM", 14, True, ACCENT, 12, first=True)
    add_para(tf, "AI Engineering Starter Kit", 40, True, FG, 14)
    add_para(tf, "How we divide engineering labor, and which commands actually do that work.", 22, False, MUTED)
    notes(s, "Open with the room: who has already run ./ask, who has only used chat. This hour is method first, then the command surface. The moons demo is one pointer at the end, not the lab.")

    # 2 agenda
    s = new_slide(prs)
    kicker_title(s, "Agenda", "How the hour is split")
    add_table(s, [
        ["Block", "Minutes", "Focus"],
        ["Method", "~45", "Labor, ownership, Explore, pipeline, evidence"],
        ["Tooling", "~30", "./ask, workstreams, skills, Cursor binding"],
        ["Demo", "~5", "Where the facilitator script lives, and what it proves"],
        ["Discussion", "~10", "What we would try on a real product repo"],
    ], top=2.4, height=3.8, col_w=[2.2, 1.8, 8.0])
    notes(s, "Protect the tooling block. Teams often spend the whole slot on philosophy and still leave setup / install / prepare mixed up.")

    # 3 what
    s = new_slide(prs)
    kicker_title(s, "What this is", "A protocol you copy into a software repo")
    tf = body_box(s)
    add_para(tf, "Portable repository protocol for delegating engineering labor to AI agents while the human keeps ownership of intent, policy, and acceptance.", 20, first=True)
    add_para(tf, "Cursor is the first-class runtime binding. The protocol stays copyable into ordinary software repos.", 20)
    add_para(tf, "The kit is Guide + Build Spec + stage contracts + small scripts + pinned Community Skills. It is not a multi-agent runtime product.", 20)
    notes(s, "Correct the category if someone says agent platform. We ship documents, contracts, and a thin dispatcher. Phases 1-2 of the Build Spec are what this repository ships.")

    # 4 question
    s = new_slide(prs)
    kicker_title(s, "The problem", "The Guide's central question")
    tf = body_box(s)
    add_para(tf, "Which engineering labor should be delegated, which judgment should remain human, what authority does each actor have, what evidence is required, and how can the resulting work remain traceable?", 26, False, FG, 12, first=True)
    notes(s, "Read the quote once. A conventional developer already does understand, clarify, design, plan, implement, review, test, accept. Agents can take slices of that. The kit exists so those slices stay named.")

    # 5 labor
    s = new_slide(prs)
    kicker_title(s, "Division of labor", "Engineering labor is several classes of work")
    tf = body_box(s, 2.2, 5)
    add_para(tf, "", 1, first=True)
    for line in [
        "Execution: write code, edit files, run commands",
        "Cognitive: compare alternatives, build a plan",
        "Judgment: decide what is appropriate under uncertainty",
        "Verification: check a claim against evidence",
        "Coordination: pass structured outputs and keep state",
        "Governance: who may decide or act, and when to escalate",
    ]:
        add_bullet(tf, line, 20)
    add_para(tf, "AI can perform some amount of all of these. The practical question is where delegation stays trustworthy and economically sensible.", 18, False, MUTED, 8)
    notes(s, "Do not rush this list. Ask the room which class they already hand to an agent, and which they still do themselves after the agent finishes.")

    # 6 five words
    s = new_slide(prs)
    kicker_title(s, "Do not collapse these", "Five questions that stay separate")
    add_table(s, [
        ["Word", "Asks"],
        ["Labor", "Who performs the work?"],
        ["Judgment", "Who decides what is correct, appropriate, or preferable?"],
        ["Capability", "What can this actor technically do?"],
        ["Authority", "What is this actor permitted to decide or enact?"],
        ["Accountability", "Who is responsible for the consequences?"],
    ], top=2.3, height=4.5, col_w=[3.0, 9.0])
    notes(s, "Capability is the one people mix with authority. An agent that can run a production migration still may not be allowed to.")

    # 7 migration
    s = new_slide(prs)
    kicker_title(s, "Example", "A database migration")
    tf = body_box(s)
    add_para(tf, "Labor          →  AI prepares migration", 20, False, FG, 6, first=True)
    add_para(tf, "Judgment       →  AI analyzes expected impact", 20, False, FG, 6)
    add_para(tf, "Capability     →  tool can execute migration", 20, False, FG, 6)
    add_para(tf, "Authority      →  human approval required for production", 20, False, FG, 6)
    add_para(tf, "Accountability →  human/team", 20, False, FG, 14)
    add_para(tf, "Delegating labor does not automatically delegate ownership.", 22, True, ACCENT)
    notes(s, "Stay on the last sentence. If the room has a recent prod scare, use that instead of inventing one.")

    # 8 ownership
    s = new_slide(prs)
    kicker_title(s, "Ownership", "Own the system that turns intent into accepted software", 28)
    tf = body_box(s)
    add_para(tf, "As implementation labor moves to agents, code-level ownership can shrink. Engineering ownership does not have to disappear with it.", 20, first=True)
    add_para(tf, "You remain responsible for What/Why, constraints, acceptance criteria, architecture boundaries, delegation policy, escalation rules, evidence policy, reusable methods, decision memory, and provenance.", 20)
    add_para(tf, "You can reuse a grilling skill or a spec method without having authored it. You still own the decision to rely on it here, and the consequences.", 20)
    notes(s, "PostgreSQL analogy from the Guide: you use it without claiming you built it. Skills are weaker than that, because they are not deterministic engines. Treat them as methodology dependencies.")

    # 9 role
    s = new_slide(prs)
    kicker_title(s, "Role", "This is still an engineering job")
    tf = body_box(s)
    add_para(tf, "A Product Owner may primarily own What, Why, and business priority.", 20, first=True)
    add_para(tf, "An engineering-system owner also governs technical constraints, architecture, acceptance evidence, verification policy, delegation boundaries, escalation, method composition, decision memory, and provenance of results.", 20)
    add_para(tf, "You can know less about a given diff and more about the system that produced and accepted it. That changes the level of ownership. It does not automatically make the role superior.", 20)
    notes(s, "If someone hears I just write tickets now, stop and reread this slide. The kit is built against that failure mode.")

    # 10 explore
    s = new_slide(prs)
    kicker_title(s, "Workflow", "Explore when the destination is foggy")
    tf = body_box(s)
    add_para(tf, "00 Explore charts decisions, research, and cheap prototypes until What/Why can be owned. It produces decisions and clarity. It does not produce accepted product software by itself.", 20, first=True)
    add_para(tf, "Skip Explore when the destination is already sharp enough for Intent. That is a real skip: no explore-map.md.", 20)
    add_para(tf, "Do not stuff R&D into Implement.", 20)
    notes(s, "Free chat in this repo: announce 00 vs 01 and wait. /00-explore starts Explore with no second-guess. A foggy keep-track-of-experiments seed is Path B in the demo plan; we will only point at that later.")

    # 11 pipeline
    s = new_slide(prs)
    kicker_title(s, "Workflow", "The Engineering Pipeline is 01-10")
    tf = body_box(s)
    add_para(tf, "01 Grill → 02 Spec → 03 Spec Challenge", 22, True, FG, 4, first=True)
    add_para(tf, "04 Spec Change (interrupt)", 22, True, FG, 4)
    add_para(tf, "05 Plan → 06 Implement → 07 Review → 08 Refactor", 22, True, FG, 4)
    add_para(tf, "09 Verify → 10 Accept", 22, True, FG, 14)
    add_para(tf, "Each next stage stands on the previous artifact. After one \"defaults OK,\" you skip extra blessings, not the documents. Accept is the second confirm.", 18)
    add_para(tf, "/off-path (or \"just code\") leaves the path for this chat only. A new chat starts on-path.", 18)
    notes(s, "Guidance, not a lock. Still hard: dirty tree, silent stash/reset, fake verify/accept, silent What/Why change. If review finds the spec semantically wrong, run Spec Change. If the destination itself was wrong, return to Explore.")

    # 12 grill
    s = new_slide(prs)
    kicker_title(s, "Grill and spec", "Grill reduces ambiguity. Challenge asks if the spec is the right problem.", 26)
    tf = body_box(s, 2.4)
    add_para(tf, "A Grill agent that only restates \"make cancellation fast\" has not done the job. Alternatives, tradeoffs, and failure modes have to be visible before \"all ok.\"", 20, first=True)
    add_para(tf, "A specification challenge asks whether the spec is a faithful representation of the intended problem. Coherent is not the same as correct.", 20)
    add_para(tf, "An implementation problem may generate a spec-change proposal. The implementer must not silently edit the accepted spec to make the code easier.", 20)
    notes(s, "Load-bearing questions only. Trivia and facts already in the repo stay out. Skill-before-grill: propose extra Community Skills that would change What/Why, ask before preparing them, pin accepted ones.")

    # 13 evidence
    s = new_slide(prs)
    kicker_title(s, "Evidence", "Verification is claim-dependent")
    tf = body_box(s)
    add_para(tf, "Do not make the implementing agent the sole judge of its own correctness. For important claims, prefer evidence whose failure mode differs from the agent that wrote the code.", 20, first=True)
    add_para(tf, "A type check, a behavioral test, an architectural check, a benchmark, and a formal proof answer different claims. None of them is universally stronger.", 20)
    add_para(tf, "Acceptance can be delegated as labor. Ultimate authority need not be. The gap between lots of autonomous changes and few strong evidence packages is acceptance debt.", 20)
    notes(s, "Three agents are not three independent reviewers if they share the same context and failure modes. Mention that only if the room starts treating a second model saying LGTM as verify.")

    # 14 provenance
    s = new_slide(prs)
    kicker_title(s, "Provenance", "Store engineering state, not every token")
    tf = body_box(s)
    add_para(tf, "Durable state: intent and spec, policy and skill versions, the code commit, the verification result, the acceptance decision.", 20, first=True)
    add_para(tf, "Every material experiment or benchmark should identify the exact commit that produced it.", 20)
    add_para(tf, "Git invariants: start from a clean tree; one plan per agent/<work-id> branch; do not pile a new task on another task's uncommitted work; commit meaningful states; record result → exact commit.", 20)
    notes(s, "This is the bridge into tooling. The scripts exist to make these invariants cheap to obey. Raw prompt dumps do not belong in git by default.")

    # 15 operating
    s = new_slide(prs)
    kicker_title(s, "Operating rule", "Delegate the bounded work. Keep the consequential calls.", 28)
    tf = body_box(s)
    add_para(tf, "Delegate labor aggressively where the work is bounded, reversible, and verifiable; preserve human judgment and authority where intent, trade-offs, risk, or irreversible consequences dominate; and move critical constraints from probabilistic instructions into deterministic enforcement whenever practical.", 20, first=True)
    add_para(tf, "Repeated failures should change the system (a check, a rule, a better spec template), not only the next prompt.", 20)
    notes(s, "Hierarchy from the Guide: better prompt → structured procedure → deterministic check → architectural constraint. Then switch to tooling.")

    # 16 layout
    s = new_slide(prs)
    kicker_title(s, "Tooling", "What lands in a product repo")
    tf = body_box(s)
    add_para(tf, "Kit package      _ask/     protocol, scripts, kit tests, kit-author docs", 20, False, FG, 8, first=True)
    add_para(tf, "Adapter          ask, AGENTS.md, .cursor/", 20, False, FG, 8)
    add_para(tf, "Product state    specs/, work/", 20, False, FG, 8)
    add_para(tf, "Your app         docs/, scripts/, tests/, src/ stay yours", 20, False, FG, 16)
    add_para(tf, "./ask is the only root command. It execs _ask/scripts/. Agents must not run ./ask setup.", 20)
    notes(s, "Clone or ./ask install into your app repo. Upgrade refreshes kit-owned paths from an explicit version. Consumer-owned: skill manifest, policies, local overlays.")

    # 17 three verbs
    s = new_slide(prs)
    kicker_title(s, "The confusing three", "Three verbs, three objects")
    add_table(s, [
        ["Command", "Object", "Who"],
        ["./ask install <repo>", "Kit files: _ask/, ask, AGENTS.md, .cursor/", "Agent or human. Target must already be a git repo. Leaves docs/, scripts/, tests/, src/ alone."],
        ["./ask prepare", "Pinned Community Skills from _ask/skills/manifest.yaml", "Agent or human. Refuses revision: latest. Bodies land in .agents/skills/ (gitignored)."],
        ["./ask setup", "Your tracker + Cursor MCP stubs", "You, on a TTY. Writes gitignored .ask.env. Agents must not run it."],
    ], top=2.15, height=3.6, col_w=[3.2, 4.6, 4.2])
    box = slide_footer = s.shapes.add_textbox(Inches(0.7), Inches(6.0), Inches(12), Inches(1.1))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    _set_run(r, "./ask sync is a fourth verb: regenerate .cursor/skills and .cursor/commands from _ask/agents/. It does not copy the kit and it does not fetch skills.", 16, False, MUTED)
    notes(s, "Stay here. Quiz: I cloned this repo. Do I install? No. I want grilling on disk. Prepare. I want Jira in Cursor. You run setup. askit on PATH: in a git repo without ./ask, confirm, then overlay (install). Later runs wrap local ./ask. askit setup is the wizard after the repo already has the kit.")

    # 18 sequences
    s = new_slide(prs)
    kicker_title(s, "Sequences", "Which list you are on")
    tf = body_box(s)
    add_para(tf, "Repo already has the kit (this one, or after overlay):", 20, True, first=True)
    add_para(tf, "1. ./ask prepare", 20)
    add_para(tf, "2. ./ask sync", 20)
    add_para(tf, "3. Work. Skip install. Skip setup unless you want the wizard.", 20, False, FG, 16)
    add_para(tf, "Adding the kit to a different app repo:", 20, True)
    add_para(tf, "1. ./ask install ../my-app  or  askit first run", 20)
    add_para(tf, "2. In that repo: prepare, then sync", 20)
    add_para(tf, "3. You run setup only for tracker/MCP", 20)
    notes(s, "Demo prerequisites follow the first list. The demo encore is a dry-run install into a temp repo. Do not install this repo onto itself.")

    # 19 workstreams
    s = new_slide(prs)
    kicker_title(s, "Workstreams", "One plan, one branch, commits as you go")
    tf = body_box(s)
    add_para(tf, "./ask start-work <work-id> creates agent/<work-id> and seeds work/<work-id>/. It refuses a dirty tree. It does not seed explore-map.md.", 20, first=True)
    add_para(tf, "On that branch, commit each meaningful step. Do not wait to be asked. Push, force-push, amend of pushed commits, and merge to main still need a human.", 20)
    add_para(tf, "./ask status lists live agent/* and archived work/* on the default branch. The current checkout is not the board.", 20)
    notes(s, "Serialize related branches that would edit the same files. Mid-work discovery goes in .later/<slug>.md (gitignored card), not a second live workstream in the same session.")

    # 20 commands
    s = new_slide(prs)
    kicker_title(s, "Command map", "What you will type after the kit is in")
    add_table(s, [
        ["Command", "Job"],
        ["./ask check-clean", "Refuse if the tree is dirty"],
        ["./ask start-work", "Branch + seed artifacts"],
        ["./ask check-workstream", "Preconditions before implement"],
        ["./ask verify", "Run checks; print commit SHA"],
        ["./ask record-result", "Workstream provenance (needs --commit-sha)"],
        ["./ask record-run", "Experiment provenance; SHA must be HEAD; tree must be clean"],
        ["./ask upgrade --version", "Refresh kit-owned files from an explicit tag or SHA"],
    ], top=2.2, height=4.7, col_w=[4.2, 7.8])
    notes(s, "Help text is ./ask with no args, -h, or help. Same text from askit once a repo already has the kit.")

    # 21 skills
    s = new_slide(prs)
    kicker_title(s, "Skills and Cursor", "Pins, prepare, thin binding")
    tf = body_box(s)
    add_para(tf, "Community Skills are declared in _ask/skills/manifest.yaml with an explicit revision. Discovery can start at skills.sh. The project owns the pin.", 20, first=True)
    add_para(tf, "Capability is not authority. A rule is not enforcement. A skill is not a guarantee. Move critical constraints into hooks, scripts, and CI when you can.", 20)
    add_para(tf, "Cursor rules point at protocol. ./ask sync writes .cursor/skills and .cursor/commands from _ask/agents/. Do not treat generated projections as the source of truth.", 20)
    notes(s, "Required pins in this repo today include wayfinder, grilling, and humanizer. developing-with-streamlit is optional. Never vendor skill trees; never revision: latest.")

    # 22 demo
    s = new_slide(prs)
    kicker_title(s, "Demo", "A facilitator script exists if you want the lab later", 28)
    tf = body_box(s)
    add_para(tf, "Script: _ask/docs/demo/end-to-end-plan.md. About 45-90 minutes for Path A. Vehicle: SHA-bound moons MLP runs.", 20, first=True)
    add_para(tf, "What it proves: durable intent and spec; clean tree + agent/<work-id>; ./ask record-run so each metric cites path + git SHA; spec changes go through Spec Change; skills come from a pin + prepare.", 20)
    add_para(tf, "After that lab you should be able to answer: which experiment, which metric, which SHA, which artifact path, who accepted the workstream. The registry is the scoreboard.", 20)
    notes(s, "Do not run training here. If someone wants the lab, schedule Path A. Mention Path B only as the foggy-seed variant. Interrupts: dirty tree, weakening acceptance criteria, spec semantically wrong, overlapping branches.")

    # 23 this week
    s = new_slide(prs)
    kicker_title(s, "This week", "A conservative first pass")
    tf = body_box(s)
    add_para(tf, "Read root AGENTS.md. Run ./ask prepare and ./ask sync in a repo that already has the kit.", 20, first=True)
    add_para(tf, "One workstream: clean tree, dedicated branch, grill What/Why, write the artifacts, commit as you go, ./ask verify, record the result against HEAD, accept with a SHA.", 20)
    add_para(tf, "The kit does not assume one model is enough, that several agents are independent reviewers, that a long rule file is formal governance, or that AI may silently redefine requirements.", 20)
    notes(s, "Close on the practical sequence from Guide section 35 if you have time. Then open the floor: where would this break on our current repos?")

    # 24 discussion
    s = new_slide(prs)
    tf = body_box(s, 2.8, 3.5)
    add_para(tf, "DISCUSSION", 14, True, ACCENT, 12, first=True)
    add_para(tf, "Where would you spend human judgment first?", 36, True, FG, 16)
    add_para(tf, "Intent, irreversible changes, and evidence policy are the usual starting points. A silent spec rewrite from last month is a concrete one.", 20, False, MUTED)
    notes(s, "Prompts if the room is quiet: which command would you have run last week that was actually a different object? Who owns Accept on your team? What would you pin in the manifest first?")

    prs.save(OUT)
    print("wrote", OUT, "slides", len(prs.slides))


if __name__ == "__main__":
    main()
