---

description: "Task list for Phase I Todo Console Application"
---

# Tasks: Todo Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, quickstart.md

**Tests**: This feature does NOT require automated tests. Manual testing workflow is documented in quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (this project uses single project structure)
- Paths shown below use absolute references starting from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure (src/, src/models/, src/skills/, tests/)
- [ ] T002 [P] Initialize Python package markers (__init__.py files in src/, src/models/, tests/)
- [ ] T003 [P] Create README.md with project description and setup instructions
- [ ] T004 [P] Create requirements.txt (empty for Phase I, but good practice)
- [ ] T005 [P] Create .gitignore for Python projects (exclude __pycache__, .venv/, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Create Task model with type alias and create_task() function in src/models/task.py
- [ ] T007 [P] Create utility module with validation functions in src/utils.py
- [ ] T008 Initialize in-memory task list in src/task_manager.py
- [ ] T009 [P] Implement _generate_next_id() helper function in src/task_manager.py
- [ ] T010 [P] Implement _find_task_by_id() helper function in src/task_manager.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks with titles/descriptions and view all tasks in the list

**Independent Test**: Launch app, add 3 tasks with different titles and descriptions, view the complete task list, verify all details displayed with status indicators (✗ for incomplete)

### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement add_task() function in src/task_manager.py
- [ ] T012 [P] [US1] Implement view_tasks() function in src/task_manager.py
- [ ] T013 [P] [US1] Implement format_task_display() function in src/utils.py
- [ ] T014 [P] [US1] Implement format_status_indicator() function in src/utils.py
- [ ] T015 [US1] Create main menu display function display_menu() in src/main.py
- [ ] T016 [US1] Implement get_menu_choice() function for menu input in src/main.py
- [ ] T017 [US1] Implement handle_add_task() function in src/main.py (depends on T011)
- [ ] T018 [US1] Implement handle_view_tasks() function in src/main.py (depends on T012, T013, T014)
- [ ] T019 [US1] Create main_loop() function with menu loop in src/main.py (depends on T015, T016, T017, T018)
- [ ] T020 [US1] Add main() entry point with if __name__ == "__main__" block in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can add and view tasks.

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to toggle task completion status between incomplete and complete

**Independent Test**: Add tasks, mark task ID 1 as complete, view tasks to confirm status changed to ✓, mark task ID 1 again to toggle back to ✗

### Implementation for User Story 2

- [ ] T021 [P] [US2] Implement mark_complete() function in src/task_manager.py
- [ ] T022 [US2] Implement handle_mark_complete() function in src/main.py (depends on T021)
- [ ] T023 [US2] Add "Mark Complete" option to menu and route in main_loop() in src/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can add, view, and mark tasks complete.

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to update task titles and/or descriptions by ID

**Independent Test**: Add task "Buy groceries", update to "Buy groceries and supplies" with new description, view tasks to confirm changes applied

### Implementation for User Story 3

- [ ] T024 [P] [US3] Implement update_task() function in src/task_manager.py
- [ ] T025 [US3] Implement handle_update_task() function in src/main.py (depends on T024)
- [ ] T026 [US3] Add "Update Task" option to menu and route in main_loop() in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can add, view, mark complete, and update tasks.

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to remove tasks from the list by ID

**Independent Test**: Add 3 tasks, delete task ID 2, view tasks to confirm only 2 tasks remain and ID 2 is gone

### Implementation for User Story 4

- [ ] T027 [P] [US4] Implement delete_task() function in src/task_manager.py
- [ ] T028 [US4] Implement handle_delete_task() function in src/main.py (depends on T027)
- [ ] T029 [US4] Add "Delete Task" option to menu and route in main_loop() in src/main.py

**Checkpoint**: At this point, all CRUD operations are complete. Users can add, view, update, delete, and mark tasks complete.

---

## Phase 7: User Story 5 - Exit Application (Priority: P5)

**Goal**: Provide a clear, graceful way to exit the application

**Independent Test**: Select "Exit" option from menu, verify goodbye message displayed and application terminates cleanly without errors

### Implementation for User Story 5

- [ ] T030 [US5] Create handle_exit() function with goodbye message in src/main.py
- [ ] T031 [US5] Add "Exit" option to menu and route in main_loop() in src/main.py
- [ ] T032 [US5] Implement clean exit logic (break from menu loop) in src/main.py

**Checkpoint**: All user stories complete. Application is fully functional with all 5 core features.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories or enhance overall quality

- [ ] T033 [P] Add comprehensive docstrings to all public functions in src/task_manager.py
- [ ] T034 [P] Add comprehensive docstrings to all public functions in src/main.py
- [ ] T035 [P] Add comprehensive docstrings to all utility functions in src/utils.py
- [ ] T036 [P] Verify PEP 8 compliance across all source files (line length, naming, spacing)
- [ ] T037 [P] Verify type hints on all function parameters and return values
- [ ] T038 Update README.md with complete usage guide and examples
- [ ] T039 [P] Add input validation for get_int_input() helper in src/utils.py
- [ ] T040 [P] Add validate_title() function in src/utils.py
- [ ] T041 [P] Add validate_task_id() function in src/utils.py
- [ ] T042 Run manual testing workflow from quickstart.md and verify all 11 test scenarios pass
- [ ] T043 Test edge cases: empty titles, invalid IDs, invalid menu choices, empty task list
- [ ] T044 Verify error messages are clear and actionable for all failure scenarios
- [ ] T045 Final code review for SRP and DRY principles

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed) or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tasks within a user story should be executed in order (except those marked [P])
- Tasks marked [P] can run in parallel within the same phase
- Complete all tasks in a user story phase before marking that story complete

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks marked [P] can run in parallel
- **Phase 2 (Foundational)**: Tasks T006, T007, T009, T010 can run in parallel
- **Phase 3 (US1)**: Tasks T011-T014 can run in parallel
- **Phase 4 (US2)**: Task T021 independent, can start immediately after Phase 2
- **Phase 5 (US3)**: Task T024 independent, can start immediately after Phase 2
- **Phase 6 (US4)**: Task T027 independent, can start immediately after Phase 2
- **Phase 8 (Polish)**: All docstring tasks (T033-T035), validation tasks (T036-T037, T039-T041) can run in parallel

**Cross-Story Parallelism**: After Phase 2 completes, US2, US3, US4, and US5 tasks can all be worked on in parallel by different developers (each story is independent)

---

## Parallel Example: User Story 1

```bash
# After Phase 2 completes, launch these tasks in parallel for User Story 1:
Task T011: "Implement add_task() function in src/task_manager.py"
Task T012: "Implement view_tasks() function in src/task_manager.py"
Task T013: "Implement format_task_display() function in src/utils.py"
Task T014: "Implement format_status_indicator() function in src/utils.py"

# Once T011-T014 complete, continue with main.py tasks sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add and View Tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can add and view tasks

**Result**: Working MVP with core value delivery

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready ✅
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! 🎯)
3. Add User Story 2 → Test independently → Deploy/Demo (now with status tracking)
4. Add User Story 3 → Test independently → Deploy/Demo (now with editing)
5. Add User Story 4 → Test independently → Deploy/Demo (full CRUD)
6. Add User Story 5 → Test independently → Deploy/Demo (complete UX)
7. Add Polish (Phase 8) → Final quality checks → Production release

**Benefit**: Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together ✅
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T020)
   - Developer B: User Story 2 (T021-T023) in parallel
   - Developer C: User Story 3 (T024-T026) in parallel
   - Developer D: User Story 4 (T027-T029) in parallel
3. Stories complete and integrate independently
4. Team completes User Story 5 together (simple, 3 tasks)
5. Team completes Polish phase (T033-T045) in parallel

**Benefit**: Maximum parallelism while maintaining independent testability

---

## Notes

- **[P] tasks**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story] labels**: Map task to specific user story for traceability (US1-US5)
- **Each user story**: Independently completable and testable
- **No automated tests**: Manual testing workflow in quickstart.md (11 scenarios)
- **Commit strategy**: Commit after each task or logical group within a story
- **Stop at checkpoints**: Validate story independently before proceeding
- **Edge cases**: Covered in Phase 8 Polish tasks (T043-T044)

**Avoid**:
- Vague tasks (all tasks have explicit file paths)
- Same file conflicts (tasks modifying same file marked with dependencies)
- Cross-story dependencies that break independence (each story builds on Foundation, not on other stories)

---

## Summary

**Total Tasks**: 45 tasks
**Task Breakdown by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - MVP): 10 tasks
- Phase 4 (US2): 3 tasks
- Phase 5 (US3): 3 tasks
- Phase 6 (US4): 3 tasks
- Phase 7 (US5): 3 tasks
- Phase 8 (Polish): 13 tasks

**Parallel Opportunities**: 20+ tasks can run in parallel (marked with [P])

**MVP Scope** (Recommended first delivery):
- Phase 1: Setup (T001-T005)
- Phase 2: Foundational (T006-T010)
- Phase 3: User Story 1 (T011-T020)
- **Total MVP tasks**: 20 tasks

**Independent Test Criteria**:
- ✅ US1: Add 3 tasks, view all with correct details
- ✅ US2: Mark task complete, verify ✓, toggle back to ✗
- ✅ US3: Update task title/description, verify changes
- ✅ US4: Delete task by ID, verify removal
- ✅ US5: Exit app, verify clean termination

**Ready for**: `/sp.implement` to execute tasks and build the application
