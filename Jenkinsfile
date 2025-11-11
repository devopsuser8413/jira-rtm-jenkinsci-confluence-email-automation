pipeline {
    agent any

    // -------------------------------
    // Pipeline Parameters
    // -------------------------------
    parameters {
        string(name: 'JIRA_ISSUE_KEY', defaultValue: 'RD-4', description: 'Jira issue key for RTM report')
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'UAT', 'PROD'], description: 'Target environment for report generation')
    }

    // -------------------------------
    // Global Environment Variables
    // -------------------------------
    environment {
        // Jira Credentials
        JIRA_BASE        = credentials('jira-base')
        JIRA_USER        = credentials('jira-user')
        JIRA_TOKEN       = credentials('jira-token')

        // Confluence Credentials
        CONFLUENCE_BASE  = credentials('confluence-base')
        CONFLUENCE_USER  = credentials('confluence-user')
        CONFLUENCE_TOKEN = credentials('confluence-token')
        CONFLUENCE_SPACE = 'DEMO'
        CONFLUENCE_TITLE = 'RTM Test Execution Report'

        // SMTP / Email
        SMTP_USER        = credentials('smtp-user')
        SMTP_PASS        = credentials('smtp-pass')
        REPORT_FROM      = credentials('sender-email')
        REPORT_TO        = credentials('multi-receivers')

        // Paths
        REPORT_DIR       = 'report'
        PYTHONUTF8       = '1'
        PYTHONIOENCODING = 'utf-8'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {

        // -------------------------------
        // 1. Checkout Code
        // -------------------------------
        stage('Checkout Repository') {
            steps {
                echo "📦 Checking out project repository..."
                git branch: 'main',
                    url: 'https://github.com/devopsuser8413/jira-rtm-jenkinsci-confluence-email-automation.git',
                    credentialsId: 'github-credentials-demo'
            }
        }

        // -------------------------------
        // 2. Setup Python Environment
        // -------------------------------
        stage('Setup Python Environment') {
            steps {
                echo "🐍 Setting up Python virtual environment..."
                bat """
                    python -m venv .venv
                    call .venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        // -------------------------------
        // 3. Fetch Saved RTM Report from Jira
        // -------------------------------
        stage('Fetch Saved RTM Report from Jira') {
            steps {
                echo "📥 Fetching Saved RTM Report for ${params.JIRA_ISSUE_KEY} (${params.ENVIRONMENT})..."
                bat """
                    call .venv\\Scripts\\activate
                    python scripts/fetch_saved_rtm_report.py
                """
            }
        }

        // -------------------------------
        // 4. Publish Report to Confluence
        // -------------------------------
        stage('Publish Report to Confluence') {
            steps {
                echo "📤 Uploading reports to Confluence..."
                bat """
                    call .venv\\Scripts\\activate
                    python scripts/publish_confluence.py
                """
            }
        }

        // -------------------------------
        // 5. Send Email Notification
        // -------------------------------
        stage('Send Email Notification') {
            steps {
                echo "📧 Sending RTM report via email..."
                bat """
                    call .venv\\Scripts\\activate
                    python scripts/send_email.py
                """
            }
        }
    }

    // -------------------------------
    // Post Actions
    // -------------------------------
    post {
        always {
            echo "🗂 Archiving RTM reports..."
            archiveArtifacts artifacts: 'report/*.html, report/*.pdf', fingerprint: true
        }
        success {
            echo "✅ RTM Test Execution report for ${params.JIRA_ISSUE_KEY} (${params.ENVIRONMENT}) completed successfully."
        }
        failure {
            echo "❌ Pipeline failed during RTM report processing."
        }
    }
}
