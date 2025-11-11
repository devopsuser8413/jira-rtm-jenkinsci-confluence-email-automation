pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    // ---------------------------------------
    // 📦 Environment Variables
    // ---------------------------------------
    environment {
        // --- Jira Credentials ---
        JIRA_BASE        = credentials('jira-base')           // e.g. https://yourdomain.atlassian.net
        JIRA_USER        = credentials('jira-user')           // Atlassian account email
        JIRA_TOKEN       = credentials('jira-token')      // Jira API token

        // --- Confluence Credentials ---
        CONFLUENCE_BASE  = credentials('confluence-base')
        CONFLUENCE_USER  = credentials('confluence-user')
        CONFLUENCE_TOKEN = credentials('confluence-token')
        CONFLUENCE_SPACE = 'DEMO'
        CONFLUENCE_TITLE = 'RTM Test Execution Report'

        // --- Email Credentials ---
        SMTP_USER        = credentials('smtp-user')
        SMTP_PASS        = credentials('smtp-pass')
        REPORT_FROM      = credentials('sender-email')
        REPORT_TO        = credentials('multi-receivers')

        // --- Project Paths ---
        REPORT_DIR       = 'report'
        REPORT_HTML      = "${REPORT_DIR}/rtm_execution_report.html"
        REPORT_PDF       = "${REPORT_DIR}/rtm_execution_report.pdf"
        VENV_PATH        = '.venv'

        // --- Python Encoding ---
        PYTHONUTF8       = '1'
        PYTHONIOENCODING = 'utf-8'
    }

    // ---------------------------------------
    // 🧩 Build Parameters
    // ---------------------------------------
    parameters {
        string(
            name: 'JIRA_ISSUE_KEY',
            defaultValue: 'EMP-TE-01',
            description: 'Enter Jira RTM Test Execution Key (e.g. EMP-TE-01)'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'QA', 'UAT', 'PROD'],
            description: 'Select the target test environment'
        )
    }

    // ---------------------------------------
    // 🧱 Pipeline Stages
    // ---------------------------------------
    stages {

        // ------------------ 1. Checkout ------------------
        stage('Checkout Repository') {
            steps {
                echo "Checking out project repository..."
                git branch: 'main', url: 'https://github.com/devopsuser8413/jira-rtm-jenkinsci-confluence-email-automation.git'
            }
        }

        // ------------------ 2. Python Setup ------------------
        stage('Setup Python Environment') {
            steps {
                echo "Setting up Python virtual environment..."
                bat """
                python -m venv %VENV_PATH%
                call %VENV_PATH%\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                """
            }
        }

        // ------------------ 3. Fetch RTM Data ------------------
        stage('Fetch RTM Test Execution Data') {
            steps {
                echo "Fetching RTM Execution report for ${params.JIRA_ISSUE_KEY} in ${params.ENVIRONMENT}..."
                bat """
                call %VENV_PATH%\\Scripts\\activate
                python scripts\\fetch_rtm_execution.py ^
                    "%JIRA_BASE%" ^
                    "%JIRA_USER%" ^
                    "%JIRA_TOKEN%" ^
                    "${params.JIRA_ISSUE_KEY}" ^
                    "${params.ENVIRONMENT}"
                """
            }
        }

        // ------------------ 4. Publish to Confluence ------------------
        stage('Publish Report to Confluence') {
            steps {
                echo "Uploading HTML & PDF reports to Confluence..."
                bat """
                call %VENV_PATH%\\Scripts\\activate
                python scripts\\upload_confluence.py
                """
            }
        }

        // ------------------ 5. Email Notification ------------------
        stage('Send Email Notification') {
            steps {
                echo "Sending email notification to stakeholders..."
                emailext(
                    subject: "RTM Test Execution Report: ${params.JIRA_ISSUE_KEY} (${params.ENVIRONMENT})",
                    body: """
                    <p>Hello Team,</p>
                    <p>The <b>RTM Test Execution Report</b> for <b>${params.JIRA_ISSUE_KEY}</b> in environment <b>${params.ENVIRONMENT}</b> has been generated successfully.</p>
                    <p>The report has been uploaded to Confluence and is attached below for your reference.</p>
                    <br>
                    <p>Regards,<br>Jenkins RTM Automation</p>
                    """,
                    to: "${REPORT_TO}",
                    from: "${REPORT_FROM}",
                    attachmentsPattern: "${REPORT_HTML}, ${REPORT_PDF}",
                    mimeType: 'text/html'
                )
            }
        }
    }

    // ---------------------------------------
    // 🧹 Post Actions
    // ---------------------------------------
    post {
        always {
            archiveArtifacts artifacts: 'report/*', fingerprint: true
            echo "Artifacts archived for ${params.JIRA_ISSUE_KEY}"
        }
        success {
            echo "✅ RTM Test Execution report for ${params.JIRA_ISSUE_KEY} completed successfully."
        }
        failure {
            echo "❌ RTM pipeline failed. Check console logs for error details."
        }
    }
}
