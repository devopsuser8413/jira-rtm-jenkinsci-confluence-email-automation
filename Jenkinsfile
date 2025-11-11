pipeline {
    agent any

    parameters {
        string(name: 'JIRA_ISSUE_KEY', defaultValue: 'RD-4', description: 'Enter Jira Issue Key')
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'QA', 'UAT', 'PROD'], description: 'Select the environment')
        string(name: 'REPORT_NAME', defaultValue: 'Test Execution Summary', description: 'Enter Saved Report Name in RTM')
    }

    environment {
        // -----------------------
        // Jira Configuration
        // -----------------------
        JIRA_BASE      = credentials('jira-base')      // e.g. https://devopsuser8413-1761792468908.atlassian.net
        JIRA_USER      = credentials('jira-user')
        JIRA_TOKEN     = credentials('jira-token')
        PROJECT_KEY    = 'RD'

        // -----------------------
        // Confluence Configuration
        // -----------------------
        CONFLUENCE_BASE  = credentials('confluence-base')
        CONFLUENCE_USER  = credentials('confluence-user')
        CONFLUENCE_TOKEN = credentials('confluence-token')
        CONFLUENCE_SPACE = 'DEMO'
        CONFLUENCE_TITLE = 'RTM Test Execution Report'

        // -----------------------
        // Email Configuration
        // -----------------------
        SMTP_HOST   = 'smtp.gmail.com'
        SMTP_PORT   = '587'
        SMTP_USER   = credentials('smtp-user')
        SMTP_PASS   = credentials('smtp-pass')
        REPORT_FROM = credentials('sender-email')
        REPORT_TO   = credentials('multi-receivers')

        // -----------------------
        // Python / Report
        // -----------------------
        REPORT_DIR   = 'report'
        VENV_PATH    = '.venv'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {

        stage('Checkout Repository') {
            steps {
                echo "📦 Checking out project repository..."
                git branch: 'main', url: 'https://github.com/devopsuser8413/jira-rtm-jenkinsci-confluence-email-automation.git', credentialsId: 'github-credentials-demo'
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "🐍 Setting up Python virtual environment..."
                bat '''
                    python -m venv %VENV_PATH%
                    call %VENV_PATH%\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Fetch Saved RTM Report from Jira') {
            steps {
                echo "📄 Fetching Saved RTM Report for ${params.JIRA_ISSUE_KEY} (${params.ENVIRONMENT})..."
                bat """
                    call %VENV_PATH%\\Scripts\\activate
                    python scripts\\fetch_saved_rtm_report.py %JIRA_BASE% %JIRA_USER% %JIRA_TOKEN% %PROJECT_KEY% "%REPORT_NAME%"
                """
            }
        }

        stage('Publish Report to Confluence') {
            when {
                expression { fileExists("${REPORT_DIR}/rtm_saved_report_*.pdf") }
            }
            steps {
                echo "🌀 Uploading Saved RTM Report to Confluence..."
                bat """
                    call %VENV_PATH%\\Scripts\\activate
                    python scripts\\upload_to_confluence.py
                """
            }
        }

        stage('Send Email Notification') {
            when {
                expression { fileExists("${REPORT_DIR}/rtm_saved_report_*.pdf") }
            }
            steps {
                echo "📧 Sending email notification via Python..."
                bat """
                    call %VENV_PATH%\\Scripts\\activate
                    python scripts\\send_email.py "%JIRA_ISSUE_KEY%" "%ENVIRONMENT%"
                """
            }
        }
    }

    post {
        success {
            echo "✅ RTM Saved Report processing completed successfully."
            archiveArtifacts artifacts: 'report/*.pdf', fingerprint: true
        }
        failure {
            echo "❌ Pipeline failed during RTM report processing."
            archiveArtifacts artifacts: 'report/*.log', fingerprint: true, allowEmptyArchive: true
        }
    }
}
