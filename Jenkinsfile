pipeline {

    agent any

    // =========================================================
    // ENVIRONMENT
    // =========================================================

    environment {

        APP_NAME = 'taskflow'

        VERSION = "1.0.${BUILD_NUMBER}"

        DEPLOY_SERVER = 'your-server.example.com'

        // Branch-specific virtual environment
        // Multibranch Pipeline creates separate JOB_NAME values
        VENV_DIR = "${JENKINS_HOME}/venv/${JOB_NAME}"

        SONAR_SCANNER_HOME = tool(
            name: 'sonar-scanner',
            type: 'hudson.plugins.sonar.SonarRunnerInstallation'
        )

        SNYK_TOKEN = credentials('snyk-id')

        // Docker image
        IMAGENAME = "906353/${APP_NAME}:${VERSION}"


        // =====================================================
        // AWS ECR
        // =====================================================

        AWS_REGION = "ap-south-1"

        AWS_ACCOUNT_ID = "928341811849"

        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

        ECR_REPOSITORY = "cicd-demo"

        // GitHub repository URL
        REPOSITORY_URL = 'https://github.com/rajendraprasad10/TaskFlow.git'

    }


    // =========================================================
    // OPTIONS
    // =========================================================

    options {

        timeout(
            time: 30,
            unit: 'MINUTES'
        )

        retry(2)

        buildDiscarder(
            logRotator(
                numToKeepStr: '10'
            )
        )
    }


    // =========================================================
    // STAGES
    // =========================================================

    stages {


        // =====================================================
        // 1. CHECKOUT
        // =====================================================

        stage('Checkout') {

            steps {

                echo "========================================="
                echo "Checking out branch"
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Build : ${env.BUILD_NUMBER}"
                echo "Job   : ${env.JOB_NAME}"
                echo "========================================="

                git branch: "${env.BRANCH_NAME}",
                    // credentialsId: 'github-creds',
                    url: "${env.REPOSITORY_URL}"
            }
        }


        // =====================================================
        // 2. BUILD / PYTHON SETUP
        // =====================================================

        stage('Build') {

            steps {

                echo "Building ${env.APP_NAME}"
                echo "Version: ${env.VERSION}"

                sh '''
                    set -e

                    echo "Starting build..."

                    python3 --version


                    # =========================================
                    # CREATE VIRTUAL ENVIRONMENT
                    # =========================================

                    if [ ! -d "$VENV_DIR" ]; then

                        echo "Creating virtual environment:"
                        echo "$VENV_DIR"

                        mkdir -p "$VENV_DIR"

                        python3 -m venv "$VENV_DIR"

                    else

                        echo "Virtual environment already exists:"
                        echo "$VENV_DIR"

                    fi


                    # =========================================
                    # ACTIVATE VENV
                    # =========================================

                    . "$VENV_DIR/bin/activate"


                    # =========================================
                    # INSTALL / UPGRADE TOOLS
                    # =========================================

                    pip install --upgrade \
                        pip \
                        setuptools \
                        wheel


                    # =========================================
                    # APPLICATION DEPENDENCIES
                    # =========================================

                    if [ -f "requirements.txt" ]; then

                        echo "Installing requirements..."

                        pip install -r requirements.txt

                    else

                        echo "WARNING:"
                        echo "requirements.txt not found"

                    fi


                    # =========================================
                    # CI TOOLS
                    # =========================================

                    pip install \
                        pytest \
                        pytest-cov \
                        flake8 \
                        bandit \
                        pip-audit


                    # =========================================
                    # VERIFY
                    # =========================================

                    echo "Installed packages:"

                    pip list


                    echo "Build completed successfully"
                '''
            }
        }


        // =====================================================
        // 3. FEATURE / BUGFIX / HOTFIX CI
        // =====================================================

        stage('Feature / Bugfix / Hotfix CI') {

            when {

                expression {

                    return env.BRANCH_NAME.startsWith('feature/') ||
                           env.BRANCH_NAME.startsWith('bugfix/') ||
                           env.BRANCH_NAME.startsWith('hotfix/')
                }
            }


            stages {


                // =================================================
                // 3.1 PARALLEL CHECKS
                // =================================================

                stage('Parallel Security & Quality Checks') {

                    parallel {


                        // =============================================
                        // GITLEAKS
                        // =============================================

                        stage('Gitleaks') {

                            steps {

                                echo "Running Gitleaks..."

                                sh '''
                                    set -e

                                    gitleaks detect \
                                        --source . \
                                        --report-format json \
                                        --report-path gitleaks-report.json \
                                        --no-banner \
                                        --exit-code 1
                                '''
                            }
                        }


                        // =============================================
                        // LINT
                        // =============================================

                        stage('Lint') {

                            steps {

                                echo "Running Flake8..."

                                sh '''
                                    set -e

                                    . "$VENV_DIR/bin/activate"

                                    flake8 app tests
                                '''
                            }
                        }


                        // =============================================
                        // SAST
                        // =============================================

                        stage('SAST') {

                            steps {

                                echo "Running Bandit SAST..."

                                sh '''
                                    set -e

                                    . "$VENV_DIR/bin/activate"

                                    bandit \
                                        -r app \
                                        -f json \
                                        -o bandit-report.json
                                '''
                            }

                            post {

                                always {

                                    archiveArtifacts(
                                        artifacts: 'bandit-report.json',
                                        allowEmptyArchive: true
                                    )
                                }
                            }
                        }


                        // =============================================
                        // SCA
                        // =============================================

                        stage('SCA') {

                            steps {

                                echo "Running Dependency Scan..."

                                sh '''
                                    set -e

                                    . "$VENV_DIR/bin/activate"

                                    pip-audit \
                                        -r requirements.txt
                                '''
                            }
                        }


                        // =============================================
                        // UNIT TEST
                        // =============================================

                        stage('Unit Tests') {

                            steps {

                                echo "Running Unit Tests..."

                                sh '''
                                    set -e

                                    . "$VENV_DIR/bin/activate"

                                    pytest tests/unit \
                                        -v
                                '''
                            }
                        }
                    }
                }


                // =================================================
                // 3.2 COVERAGE
                // =================================================

                stage('Coverage') {

                    steps {

                        echo "Generating test coverage..."

                        sh '''
                            set -e

                            . "$VENV_DIR/bin/activate"

                            pytest tests/unit \
                                --cov=app \
                                --cov-report=term \
                                --cov-report=xml:coverage.xml
                        '''
                    }

                    post {

                        always {

                            archiveArtifacts(
                                artifacts: 'coverage.xml',
                                allowEmptyArchive: true
                            )
                        }
                    }
                }


                // =================================================
                // 3.3 SONARQUBE
                // =================================================

                stage('SonarQube Analysis') {

                    steps {

                        echo "Running SonarQube analysis..."

                        withSonarQubeEnv('sonarserver') {

                            sh '''
                                set -e

                                echo "Current directory:"
                                pwd

                                echo "Coverage report:"
                                ls -lh coverage.xml

                                . "$VENV_DIR/bin/activate"

                                echo "Running SonarQube Scanner..."

                                "$SONAR_SCANNER_HOME/bin/sonar-scanner"

                                echo "SonarQube analysis completed."
                            '''
                        }
                    }
                }


                // =================================================
                // 3.4 QUALITY GATE
                // =================================================

                stage('Quality Gate') {

                    steps {

                        echo "========================================="
                        echo "SONARQUBE QUALITY GATE"
                        echo "========================================="

                        timeout(
                            time: 5,
                            unit: 'MINUTES'
                        ) {

                            script {

                                def qualityGate =
                                    waitForQualityGate(
                                        abortPipeline: false
                                    )


                                echo "SonarQube Quality Gate:"
                                echo "Status: ${qualityGate.status}"


                                if (qualityGate.status != 'OK') {

                                    error(
                                        "SonarQube Quality Gate failed: ${qualityGate.status}"
                                    )
                                }


                                echo "Quality Gate PASSED."
                            }
                        }
                    }
                }
            }
        }


        // =====================================================
        // 4. DEVELOP CI/CD
        // =====================================================

        stage('Develop CI/CD') {

            when {

                expression {

                    return env.BRANCH_NAME == 'develop'
                }
            }


            stages {


                // =================================================
                // 4.1 INTEGRATION TEST
                // =================================================

                stage('Integration Tests') {

                    steps {

                        echo "Running Integration Tests..."

                        sh '''
                            set -e

                            . "$VENV_DIR/bin/activate"

                            pytest tests/integration \
                                -v
                        '''
                    }
                }


                // =================================================
                // 4.2 DOCKER BUILD
                // =================================================

                stage('Build Docker Image') {

                    steps {

                        echo "Building Docker image..."

                        sh """
                            set -e

                            docker build \
                                -t ${env.IMAGENAME} \
                                .
                        """
                    }
                }


                // =================================================
                // 4.3 SNYK CONTAINER SCAN
                // =================================================

                stage('Snyk Container Scan') {

                    steps {

                        echo "Running Snyk Container Scan..."

                        sh """
                            set -e

                            . "\$VENV_DIR/bin/activate"

                            snyk auth "\$SNYK_TOKEN"

                            snyk container monitor \
                                ${env.IMAGENAME} \
                                --file=Dockerfile \
                                --project-name=cicd-demo-container \
                                --org=cicd-demo-dev \
                                || true
                        """
                    }
                }


                // =================================================
                // 4.4 TRIVY IMAGE SCAN
                // =================================================

                stage('Trivy Image Scan') {

                    steps {

                        echo "Running Trivy Image Scan..."

                        sh """
                            set -e

                            trivy image \
                                --severity HIGH,CRITICAL \
                                ${env.IMAGENAME}
                        """
                    }
                }


                // =================================================
                // 4.5 PUSH TO AWS ECR
                // =================================================

                stage('Push to AWS ECR') {

                    steps {

                        echo "Pushing image to AWS ECR..."

                        withAWS(
                            credentials:
                                'aws-cicd-demo-user-creds',
                            region:
                                "${AWS_REGION}"
                        ) {

                            sh """

                                set -e


                                echo "Logging into AWS ECR..."

                                aws ecr get-login-password \
                                    --region ${AWS_REGION} |
                                docker login \
                                    --username AWS \
                                    --password-stdin \
                                    ${ECR_REGISTRY}


                                echo "Tagging Docker image..."

                                docker tag \
                                    ${env.IMAGENAME} \
                                    ${ECR_REGISTRY}/${ECR_REPOSITORY}:${env.VERSION}


                                echo "Pushing Docker image..."

                                docker push \
                                    ${ECR_REGISTRY}/${ECR_REPOSITORY}:${env.VERSION}


                                echo "Image pushed successfully."

                            """
                        }
                    }
                }


                // =================================================
                // 4.6 DEV DEPLOYMENT
                // =================================================

                stage('Deploy DEV') {

                    steps {

                        echo "========================================="
                        echo "DEV DEPLOYMENT"
                        echo "========================================="

                        echo "Application: ${env.APP_NAME}"
                        echo "Version: ${env.VERSION}"
                        echo "Environment: DEV"


                        sh '''

                            echo "Starting DEV deployment..."

                            chmod +x deploy.sh

                            ./deploy.sh dev

                            echo "DEV deployment completed successfully."

                        '''
                    }
                }


                // =================================================
                // 4.7 DEV API TESTS
                // =================================================

                stage('DEV API Tests') {

                    steps {

                        echo "Running DEV API / Integration tests..."

                        sh '''

                            echo "API tests go here"

                            # Example:
                            #
                            # . "$VENV_DIR/bin/activate"
                            #
                            # pytest tests/api \
                            #     -v

                        '''
                    }
                }
            }
        }


        // =====================================================
        // 5. MAIN / PRODUCTION
        // =====================================================

        stage('Production') {

            when {

                expression {

                    return env.BRANCH_NAME == 'main'
                }
            }


            stages {


                // =================================================
                // PRODUCTION VALIDATION
                // =================================================

                stage('Production Validation') {

                    steps {

                        echo "========================================="
                        echo "PRODUCTION VALIDATION"
                        echo "========================================="

                        echo "Branch: ${env.BRANCH_NAME}"
                        echo "Version: ${env.VERSION}"

                        echo "Production validation completed."
                    }
                }


                // =================================================
                // PRODUCTION DEPLOY
                // =================================================

                stage('Production Deployment') {

                    steps {

                        echo "========================================="
                        echo "PRODUCTION DEPLOYMENT"
                        echo "========================================="


                        sh '''

                            echo "Starting production deployment..."

                            chmod +x deploy.sh

                            ./deploy.sh production

                            echo "Production deployment completed successfully."

                        '''
                    }
                }
            }
        }
    }


    // =========================================================
    // POST ACTIONS
    // =========================================================

    post {

        always {

            script {

                echo "========================================="
                echo "PIPELINE CLEANUP"
                echo "========================================="

                echo "Branch: ${env.BRANCH_NAME}"

                echo "Cleaning Docker authentication..."

                sh """
                    docker logout ${ECR_REGISTRY} || true
                """
            }


            // ================================================
            // GITLEAKS REPORT
            // ================================================

            archiveArtifacts(
                artifacts: 'gitleaks-report.json',
                allowEmptyArchive: true
            )


            echo "Pipeline execution completed."


            // ================================================
            // WORKSPACE CLEANUP
            // ================================================

            cleanWs()
        }


        // =====================================================
        // SUCCESS
        // =====================================================

        success {

            echo """
            =========================================
                    PIPELINE SUCCESS
            =========================================

            Branch : ${env.BRANCH_NAME}
            Build  : ${env.BUILD_NUMBER}
            Version: ${env.VERSION}

            Pipeline completed successfully.

            =========================================
            """
        }


        // =====================================================
        // FAILURE
        // =====================================================

        failure {

            echo """
            =========================================
                    PIPELINE FAILED
            =========================================

            Branch : ${env.BRANCH_NAME}
            Build  : ${env.BUILD_NUMBER}

            Pipeline failed.

            Please check the failed stage
            and Jenkins console output.

            =========================================
            """
        }


        // =====================================================
        // UNSTABLE
        // =====================================================

        unstable {

            echo """
            =========================================
                    PIPELINE UNSTABLE
            =========================================

            Branch : ${env.BRANCH_NAME}
            Build  : ${env.BUILD_NUMBER}

            Pipeline completed with warnings.

            =========================================
            """
        }
    }
}