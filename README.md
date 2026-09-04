# Travel Booking Automation Framework

Web automation framework for a travel booking platform, designed to demonstrate professional UI test automation practices using Selenium WebDriver, Java, JUnit, Page Object Model, reporting, and CI/CD.

---

## Project Overview

This project is an automated testing framework for a travel booking web application.

The framework focuses on validating critical user journeys such as authentication, travel searches, date selection, filters, passenger configuration, booking forms, and reservation confirmation.

The project is designed as a portfolio project to demonstrate practical skills in **Software Quality Assurance, Web Automation, Test Architecture, and Continuous Integration**.

---

## Objectives

* Build a maintainable UI automation framework.
* Automate critical travel booking workflows.
* Apply the Page Object Model design pattern.
* Create reusable test components.
* Implement positive and negative test scenarios.
* Validate business rules through automated assertions.
* Generate automated test reports.
* Integrate the framework with CI/CD.
* Demonstrate professional QA practices.

---

## Application Under Test

The framework will automate an existing travel booking/demo website.

The application will be treated as the **System Under Test (SUT)** and will not be modified as part of this project.

### Main Functional Areas

*  User authentication
*  Travel search
*  Date selection
*  Passenger configuration
*  Search filters
*  Travel option selection
*  Booking information
*  Simulated payment information
*  Booking confirmation
*  Negative scenarios
*  Regression scenarios

---

## Testing Scope

### Functional Testing

Validate that the application's features behave according to their expected business rules.

### Negative Testing

Validate how the application behaves when users provide:

* Invalid credentials
* Missing information
* Invalid dates
* Invalid passenger configurations
* Incorrect form data
* Unsupported search criteria

### Smoke Testing

A lightweight suite covering the most critical flows:

1. Application availability
2. Login
3. Search
4. Result selection
5. Booking flow

### Regression Testing

Automated regression suites will verify that existing functionality continues working after application changes.

### UI Testing

Validate:

* Page navigation
* Form interactions
* Buttons
* Inputs
* Dropdowns
* Date pickers
* Search results
* Validation messages
* Booking confirmation

---

## Automation Architecture

```text
                    ┌───────────────────────┐
                    │   Travel Web App      │
                    │    System Under Test  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Selenium WebDriver │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      Page Objects     │
                    ├───────────────────────┤
                    │ LoginPage             │
                    │ SearchPage            │
                    │ ResultsPage            │
                    │ BookingPage            │
                    │ ConfirmationPage       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      JUnit Tests      │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Assertions & Logs   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Allure Reports     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    GitHub Actions     │
                    │        CI/CD          │
                    └───────────────────────┘
```

---

## Technology Stack

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| **Java**               | Programming language            |
| **Selenium WebDriver** | Web UI automation               |
| **JUnit**              | Test execution and assertions   |
| **Maven**              | Dependency and build management |
| **Page Object Model**  | Automation architecture         |
| **Allure**             | Test reporting                  |
| **Git**                | Version control                 |
| **GitHub**             | Source code management          |
| **GitHub Actions**     | CI/CD automation                |

---

## Page Object Model

Each major application page will have its own Page Object.

Example:

```text
LoginPage
    ↓
SearchPage
    ↓
ResultsPage
    ↓
BookingPage
    ↓
ConfirmationPage
```

This approach allows the framework to separate:

* Test logic
* Page interaction logic
* Locators
* Reusable components
* Test data

---

## Main E2E Scenario

### Successful Booking

```text
Open Application
       ↓
Login
       ↓
Search Destination
       ↓
Select Travel Dates
       ↓
Configure Passengers
       ↓
Execute Search
       ↓
Apply Filters
       ↓
Select Travel Option
       ↓
Enter Booking Information
       ↓
Submit Booking
       ↓
Validate Confirmation
```

---

## Example Test Scenarios

### Authentication

* Login with valid credentials
* Login with invalid credentials
* Login with empty fields
* Logout successfully

### Search

* Search using valid criteria
* Search with missing destination
* Search with invalid dates
* Search with different passenger configurations

### Filters

* Filter available results
* Combine multiple filters
* Remove filters
* Validate filtered results

### Booking

* Complete booking successfully
* Validate required fields
* Submit incomplete booking
* Validate invalid booking information
* Verify confirmation details

---

## Test Prioritization

| Priority          | Description                         |
| ----------------- | ----------------------------------- |
| **P0 - Critical** | Core booking functionality          |
| **P1 - High**     | Authentication and search           |
| **P2 - Medium**   | Filters and secondary functionality |
| **P3 - Low**      | UI validations and minor scenarios  |

---

## Test Types

The framework will include:

* Functional Testing
* UI Testing
* Positive Testing
* Negative Testing
* Smoke Testing
* Regression Testing
* End-to-End Testing
* Cross-browser Testing

---

## QA Strategy

The project follows a risk-based testing approach.

Critical business flows receive the highest automation priority.

### Critical Flow

```text
Login
  ↓
Search
  ↓
Select
  ↓
Booking
  ↓
Confirmation
```

These scenarios will be included in the smoke and regression suites.

---

## Test Reporting

The framework will generate **Allure Reports** containing:

* Test execution status
* Passed tests
* Failed tests
* Execution duration
* Test steps
* Screenshots
* Error information
* Test history

Example:

```text
Allure Report
│
├── Total Tests
├── Passed
├── Failed
├── Broken
├── Skipped
└── Execution Time
```

---

## CI/CD

GitHub Actions will execute automated tests automatically.

### Pipeline

```text
Push / Pull Request
        ↓
Checkout Repository
        ↓
Set Up Java
        ↓
Install Dependencies
        ↓
Execute Tests
        ↓
Generate Results
        ↓
Generate Allure Report
        ↓
Publish Artifacts
```

---

## Running the Tests

Clone the repository:

```bash
git clone <repository-url>
```

Navigate to the project:

```bash
cd travel-booking-automation-framework
```

Install dependencies:

```bash
mvn clean install
```

Run the complete test suite:

```bash
mvn test
```

---

## Cross-Browser Testing

The framework can be extended to execute tests against multiple browsers:

```text
Chrome
Firefox
Edge
```

Browser configuration will be managed through configuration properties rather than hard-coded values.

---

## Documentation

Additional project documentation may include:

```text
docs/
│
├── test-strategy.md
├── test-plan.md
├── test-cases.md
├── automation-strategy.md
├── bug-reports.md
└── test-execution-report.md
```

---

## Future Improvements

* [ ] Add parallel test execution
* [ ] Add Selenium Grid
* [ ] Add Docker support
* [ ] Add cross-browser execution
* [ ] Improve test data management
* [ ] Add environment configuration
* [ ] Add retry mechanism for unstable tests
* [ ] Add API automation if the application exposes APIs
* [ ] Integrate Slack/Teams notifications
* [ ] Improve Allure reporting
* [ ] Add visual regression testing

---

## Portfolio Goals

This project demonstrates practical experience with:

* Software Testing
* QA Strategy
* Test Automation
* Selenium WebDriver
* Java
* JUnit
* Page Object Model
* Test Design
* Regression Testing
* CI/CD
* Test Reporting
* Git & GitHub

The goal is to demonstrate how a QA Engineer can design, implement, execute, and maintain a professional automation framework.

---

## Project Status

 **In Development**

The framework will be progressively expanded with additional automated scenarios, reporting, CI/CD integration, and advanced automation practices.

---

## License

This project is intended for educational and portfolio purposes.
