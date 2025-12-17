# Tasks: Thai/English Realtime Voice Agent

**Input**: Design documents from `/specs/001-thai-voice-agent/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included per constitution requirement (V. Test Coverage Requirements - 80% minimum coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (src/, tests/unit/, tests/integration/)
- [x] T002 Create requirements.txt with dependencies: openai-agents[voice], sounddevice, numpy, python-dotenv, pydantic, pydantic-settings, pytest, pytest-asyncio, pytest-cov
- [x] T003 [P] Create src/__init__.py with package metadata
- [x] T004 [P] Create tests/__init__.py
- [x] T005 [P] Create tests/unit/__init__.py
- [x] T006 [P] Create tests/integration/__init__.py
- [x] T007 [P] Create .env.example with OPENAI_API_KEY placeholder and optional config vars
- [x] T008 [P] Create .gitignore with Python, .env, and IDE patterns
- [x] T009 [P] Configure pyproject.toml with ruff linting and mypy type checking

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create enums module with ConnectionState, EventType, AudioDirection, Language in src/models/__init__.py
- [x] T011 [P] Create SessionConfig model with validation in src/models/config.py
- [x] T012 [P] Create TurnDetectionConfig model with validation in src/models/config.py
- [x] T013 Create Settings class with pydantic-settings for env var loading in src/config.py
- [x] T014 Create VoiceSession model in src/models/session.py
- [x] T015 [P] Create SessionEvent model in src/models/events.py
- [x] T016 [P] Create AudioChunk model in src/models/audio.py
- [x] T017 Create custom exception classes with error codes in src/exceptions.py
- [x] T018 Create JSON logging formatter with correlation ID support in src/logging_config.py
- [x] T019 Create tests/conftest.py with shared fixtures (mock settings, sample configs)
- [x] T020 [P] Create unit tests for config validation in tests/unit/test_config.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Voice Conversation in Thai (Priority: P1) 🎯 MVP

**Goal**: Enable natural voice conversation with the AI agent in Thai language

**Independent Test**: Speak Thai to the agent and receive Thai audio responses within 500ms

### Tests for User Story 1

- [x] T021 [P] [US1] Create unit test for agent configuration in tests/unit/test_agent.py
- [x] T022 [P] [US1] Create integration test for Thai conversation flow in tests/integration/test_thai_conversation.py

### Implementation for User Story 1

- [x] T023 [US1] Create bilingual agent instructions constant in src/agent.py
- [x] T024 [US1] Implement create_realtime_agent() function with Thai/English instructions in src/agent.py
- [x] T025 [US1] Create RealtimeRunner configuration builder in src/runner.py
- [x] T026 [US1] Implement session initialization with config validation in src/runner.py
- [x] T027 [US1] Create audio input stream handler using sounddevice in src/audio.py
- [x] T028 [US1] Create audio output stream handler for playback in src/audio.py
- [x] T029 [US1] Implement main event loop that processes session events in src/main.py
- [x] T030 [US1] Add CLI argument parsing for voice, log-level, device options in src/main.py
- [x] T031 [US1] Implement graceful session startup with "Ready" message in src/main.py
- [x] T032 [US1] Implement graceful shutdown on Ctrl+C in src/main.py

**Checkpoint**: Thai voice conversation should work end-to-end

---

## Phase 4: User Story 2 - Basic Voice Conversation in English (Priority: P1)

**Goal**: Enable natural voice conversation with the AI agent in English with language detection

**Independent Test**: Speak English to the agent and receive English audio responses; switch languages mid-conversation

### Tests for User Story 2

- [x] T033 [P] [US2] Create integration test for English conversation flow in tests/integration/test_english_conversation.py
- [x] T034 [P] [US2] Create integration test for language switching in tests/integration/test_language_switch.py

### Implementation for User Story 2

- [x] T035 [US2] Enhance agent instructions to explicitly handle language detection in src/agent.py
- [x] T036 [US2] Add language detection logging to event handler in src/events.py
- [x] T037 [US2] Create ConversationTurn model for tracking exchanges in src/models/conversation.py
- [x] T038 [US2] Implement turn tracking with detected_language field in src/runner.py

**Checkpoint**: Both Thai and English conversations should work with automatic language detection

---

## Phase 5: User Story 3 - Interruption Handling (Priority: P2)

**Goal**: Allow users to interrupt the agent while it is speaking

**Independent Test**: Speak over the agent during its response and verify it stops within 200ms

### Tests for User Story 3

- [x] T039 [P] [US3] Create unit test for audio queue clearing on interrupt in tests/unit/test_audio.py
- [x] T040 [P] [US3] Create integration test for interruption handling in tests/integration/test_interruption.py

### Implementation for User Story 3

- [x] T041 [US3] Implement audio playback queue with clear() method in src/audio.py
- [x] T042 [US3] Add audio_interrupted event handler that stops playback in src/events.py
- [x] T043 [US3] Implement interrupt detection callback in audio input stream in src/audio.py
- [x] T044 [US3] Add was_interrupted flag tracking to ConversationTurn in src/models/conversation.py
- [x] T045 [US3] Log interruption events with timing metrics in src/events.py

**Checkpoint**: Interruptions should stop agent audio within 200ms

---

## Phase 6: User Story 4 - Tool Execution During Conversation (Priority: P2)

**Goal**: Enable the agent to execute function tools (like getting current time) during conversations

**Independent Test**: Ask "What time is it?" and verify the agent returns the correct current time

### Tests for User Story 4

- [x] T046 [P] [US4] Create unit test for get_current_time tool in tests/unit/test_tools.py
- [x] T047 [P] [US4] Create integration test for tool execution flow in tests/integration/test_tool_execution.py

### Implementation for User Story 4

- [x] T048 [US4] Create FunctionTool model in src/models/tools.py
- [x] T049 [US4] Implement get_current_time tool with Thailand timezone in src/tools.py
- [x] T050 [US4] Add @function_tool decorator usage for tool registration in src/tools.py
- [x] T051 [US4] Register tools with RealtimeAgent in src/agent.py
- [x] T052 [US4] Add tool_start and tool_end event handlers in src/events.py
- [x] T053 [US4] Implement tool error handling with graceful user notification in src/tools.py

**Checkpoint**: Tool execution should work in both Thai and English

---

## Phase 7: User Story 5 - Session Event Logging (Priority: P3)

**Goal**: Log all session events for debugging and analysis

**Independent Test**: Run a conversation and verify logs contain all event types with timestamps and correlation IDs

### Tests for User Story 5

- [x] T054 [P] [US5] Create unit test for event logging format in tests/unit/test_events.py
- [x] T055 [P] [US5] Create unit test for correlation ID propagation in tests/unit/test_logging.py

### Implementation for User Story 5

- [x] T056 [US5] Create comprehensive event handler registry in src/events.py
- [x] T057 [US5] Implement handler for agent_start event with agent name logging in src/events.py
- [x] T058 [US5] Implement handler for agent_end event with session duration in src/events.py
- [x] T059 [US5] Implement handler for audio events with chunk count tracking in src/events.py
- [x] T060 [US5] Implement handler for audio_end event with total duration in src/events.py
- [x] T061 [US5] Implement handler for error events with full error details in src/events.py
- [x] T062 [US5] Add session summary logging on session close in src/runner.py
- [x] T063 [US5] Implement log file output option via config in src/logging_config.py

**Checkpoint**: All events should be logged with complete information

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T064 [P] Create README.md with project overview, setup, and usage instructions
- [x] T065 [P] Update quickstart.md with actual tested commands in specs/001-thai-voice-agent/quickstart.md
- [x] T066 Run all unit tests and verify 80% coverage threshold
- [x] T067 Run all integration tests with mocked API
- [x] T068 [P] Add type hints to all public functions and run mypy
- [x] T069 [P] Run ruff linter and fix any issues
- [ ] T070 Manual end-to-end test: Thai conversation (5 turns)
- [ ] T071 Manual end-to-end test: English conversation (5 turns)
- [ ] T072 Manual end-to-end test: Interruption handling
- [ ] T073 Manual end-to-end test: Tool execution (time query)
- [x] T074 Document any issues or limitations discovered in testing

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundational (BLOCKS all user stories)
    │
    ├──────────────────────────────────────────┐
    │                                          │
    ▼                                          ▼
Phase 3: US1 (Thai)              Phase 4: US2 (English)
    │                                          │
    └──────────────┬───────────────────────────┘
                   │
    ┌──────────────┴───────────────┐
    │                              │
    ▼                              ▼
Phase 5: US3 (Interrupts)   Phase 6: US4 (Tools)
    │                              │
    └──────────────┬───────────────┘
                   │
                   ▼
           Phase 7: US5 (Logging)
                   │
                   ▼
           Phase 8: Polish
```

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase 2 - Shares agent with US1 but independently testable
- **User Story 3 (P2)**: Requires US1/US2 audio infrastructure - Builds on audio.py
- **User Story 4 (P2)**: Can start after Phase 2 - Independent tool implementation
- **User Story 5 (P3)**: Requires event infrastructure from US1-4 - Enhances existing handlers

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003-T009 (Setup): All can run in parallel
- T011-T012, T015-T016, T020 (Foundational): Can run in parallel
- T021-T022 (US1 tests): Can run in parallel
- T033-T034 (US2 tests): Can run in parallel
- T039-T040 (US3 tests): Can run in parallel
- T046-T047 (US4 tests): Can run in parallel
- T054-T055 (US5 tests): Can run in parallel
- T064-T065, T068-T069 (Polish): Can run in parallel

---

## Parallel Example: Phase 2 Foundational

```bash
# These can run in parallel (different files):
T011: Create SessionConfig model in src/models/config.py
T012: Create TurnDetectionConfig model in src/models/config.py
T015: Create SessionEvent model in src/models/events.py
T016: Create AudioChunk model in src/models/audio.py
T020: Create unit tests for config in tests/unit/test_config.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Thai conversation)
4. **STOP and VALIDATE**: Test Thai conversation independently
5. Demo if ready - this proves Thai language viability

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Thai) → Test → Demo (MVP!)
3. Add US2 (English) → Test → Demo (Bilingual!)
4. Add US3 (Interrupts) → Test → Demo (Natural conversation!)
5. Add US4 (Tools) → Test → Demo (Dynamic info!)
6. Add US5 (Logging) → Test → Complete POC

### Single Developer Strategy

Execute phases sequentially in priority order:
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tests use pytest with pytest-asyncio for async functions
- Manual E2E tests (T070-T073) require actual microphone/speaker and API key
