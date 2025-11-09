pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        PYTEST_SUMMARY = ''
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/anguzz/cicd-webex.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                echo "Checking Python installation..."
                python3 --version || echo "Python not found, installing..."
                apt-get update && apt-get install -y python3 python3-pip python3-venv
                python3 --version
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                python3 -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

stage('Run Tests') {
    steps {
        sh '''
        . ${VENV_DIR}/bin/activate
        pytest -v | tee pytest_output.txt || true
        '''
    }
}
}

 post {
    success {
        withCredentials([
            string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
            string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
        ]) {
            script {
                def summary = sh(
                    script: "tail -n 5 pytest_output.txt 2>/dev/null | grep -E 'passed|failed|error|collected' || echo 'No test summary found.'",
                    returnStdout: true
                ).trim()

                def payload = """{
                    "roomId": "${WEBEX_ROOM_ID}",
                    "markdown": "Jenkins build successful for cicd-webex project.\\n\\nTest Summary:\\n${summary.replaceAll('"', '\\\\\"')}"
                }"""

                sh """
                curl -s -X POST \
                    -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d '${payload}' \
                    https://webexapis.com/v1/messages
                """
            }
        }
    }

    failure {
        withCredentials([
            string(credentialsId: 'WEBEX_BOT_TOKEN', variable: 'WEBEX_BOT_TOKEN'),
            string(credentialsId: 'WEBEX_ROOM_ID', variable: 'WEBEX_ROOM_ID')
        ]) {
            script {
                def summary = sh(
                    script: "tail -n 5 pytest_output.txt 2>/dev/null | grep -E 'passed|failed|error|collected' || echo 'No test summary found.'",
                    returnStdout: true
                ).trim()

                def payload = """{
                    "roomId": "${WEBEX_ROOM_ID}",
                    "markdown": "Jenkins build failed for cicd-webex project.\\n\\nTest Summary:\\n${summary.replaceAll('"', '\\\\\"')}"
                }"""

                sh """
                curl -s -X POST \
                    -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d '${payload}' \
                    https://webexapis.com/v1/messages
                """
            }
        }
    }

    always {
        echo "Build completed and WebEx message sent."
    }
}
