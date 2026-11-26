# Test plan

| Item | Detail |
|---|---|
| Project | Travel Booking Automation Framework |
| Application | Restful Booker Platform, public demo at https://automationintesting.online |
| Author | Maria Jose Ospina |
| Strategy | [`test-strategy.md`](test-strategy.md) |
| Test cases | [`test-cases.md`](test-cases.md) |
| Defects | [`defects.md`](defects.md) |

## 1. Features and priorities

| Feature | Priority | Why |
|---|---|---|
| Guest booking and double booking | Critical | It is how the hotel earns money; a double booking means two guests for one room |
| Admin authentication and permissions | Critical | Every admin action and guest's personal data depends on it |
| Contact form and admin inbox | High | The only channel between guests and the hotel; holds guests' contact details |
| Room management | High | Rooms the admin creates are what guests can book |
| Booking validation (dates, guest details) | High | Prevents bookings that can never happen or cannot be contacted |
| Branding | Medium | Wrong details mislead guests, but do not block bookings |

## 2. Approach per feature

| Feature | UI | API | Integration | Postman |
|---|:---:|:---:|:---:|:---:|
| Authentication | ✅ | ✅ | | ✅ |
| Rooms | ✅ | ✅ | ✅ | ✅ |
| Guest booking | ✅ | ✅ | ✅ | ✅ |
| Contact form and inbox | ✅ | ✅ | ✅ | ✅ |
| Branding | ✅ | ✅ | ✅ | ✅ (read and rejected updates only) |

## 3. Schedule

| Phase | Content | Result |
|---|---|---|
| 1 | Framework core, admin login, rooms API, first Postman collection, CI | Done · BUG-001 |
| 2 | Guest booking in UI, API, Postman and integration | Done · BUG-002, BUG-003 |
| 3 | Contact form and admin inbox | Done · BUG-004, BUG-005 |
| 4 | Branding, admin rooms in the UI, strategy and plan, published reports | Done · BUG-006, BUG-007, BUG-008 |

## 4. Deliverables

- Automated tests: `tests/api`, `tests/ui`, `tests/integration`
- Postman collection, environment and data file: `postman/`
- Test cases, defect reports, this plan and the strategy: `docs/`
- Allure and Newman reports, published on GitHub Pages by GitHub Actions

## 5. Running the tests

| Command | What it runs |
|---|---|
| `pytest` | Every test except the ones that expose open defects |
| `pytest -m smoke` | The most critical flows only |
| `pytest -m "api"` / `-m "ui"` / `-m "integration"` | One layer |
| `pytest -m known_defect` | Only the checks that expose open defects (they fail on purpose) |
| `newman run ... --folder Auth --folder Rooms --folder Booking --folder Messages --folder Branding` | The Postman collection, as CI runs it |
| `newman run ... --folder "Known defects"` | The Postman checks that expose open defects |

## 6. Risks

See section 6 of the [test strategy](test-strategy.md): shared public demo, restarts, regular data resets and the 60-second branding cache.
