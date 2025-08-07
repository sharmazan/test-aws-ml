#!/bin/bash
set -euo pipefail

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .env file if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
else
    echo "Warning: .env file not found in $PROJECT_DIR, relying on existing environment variables"
fi

# Constants
TF_VERSION="1.5.7"
REQUIRED_TOOLS=("aws" "zip" "unzip" "wget" "pip3")
LAYER_DIR="$SCRIPT_DIR/layer"
LAYER_ZIP="$SCRIPT_DIR/layer.zip"
FUNCTION_ZIP="$SCRIPT_DIR/function.zip"
LAYER_NAME="titanic-ml-deps"
PYTHON_VERSION="python3.11"

# Check for required tools
check_requirements() {
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo "Error: $tool is not installed"
            exit 1
        fi
    done
}

# Verify AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "Error: AWS credentials not configured"
        exit 1
    fi
}

# Install Terraform if needed
install_terraform() {
    if ! command -v terraform &> /dev/null; then
        echo "Installing Terraform ${TF_VERSION}..."
        OS=$(uname | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        [ "$ARCH" = "x86_64" ] && ARCH="amd64"
        
        TEMP_DIR=$(mktemp -d)
        pushd "$TEMP_DIR" > /dev/null
        
        wget -q "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_${OS}_${ARCH}.zip" || {
            echo "Failed to download Terraform"
            exit 1
        }
        
        unzip -q "terraform_${TF_VERSION}_${OS}_${ARCH}.zip"
        chmod +x terraform
        sudo mv terraform /usr/local/bin/
        
        popd > /dev/null
        rm -rf "$TEMP_DIR"
    fi
}

# Main execution
main() {
    check_requirements
    check_aws_credentials
    install_terraform

    cd "$(dirname "$0")"

    # Create Lambda Layer
    echo "Creating Lambda Layer with dependencies..."
    
    # Create and clean layer directory
    rm -rf "$LAYER_DIR"
    mkdir -p "$LAYER_DIR/$PYTHON_VERSION"
    
    # Install only essential dependencies to the layer directory
    echo "Installing minimal Python dependencies..."
    pip3 install --target "$LAYER_DIR/$PYTHON_VERSION" \
        pandas==2.0.3 \
        numpy==1.24.3 \
        scikit-learn==1.3.0 \
        boto3==1.28.4 \
        python-dotenv==1.0.0 \
        --no-cache-dir --no-deps || {
        echo "Failed to install dependencies"
        exit 1
    }
    
    # Install dependencies separately to avoid conflicts
    pip3 install --target "$LAYER_DIR/$PYTHON_VERSION" \
        --no-deps --no-cache-dir \
        python-dateutil==2.9.0 \
        pytz==2024.1 \
        tzdata==2024.1 \
        six==1.16.0 \
        joblib==1.3.2 \
        threadpoolctl==3.1.0 || {
        echo "Failed to install dependencies"
        exit 1
    }
    
    # Remove unnecessary files to reduce size
    echo "Reducing package size..."
    find "$LAYER_DIR" -type d -name "__pycache__" -exec rm -rf {} +
    find "$LAYER_DIR" -type d -name "tests" -exec rm -rf {} +
    find "$LAYER_DIR" -type d -name "test" -exec rm -rf {} +
    find "$LAYER_DIR" -name "*.so" | grep -v "numpy" | xargs rm -f
    find "$LAYER_DIR" -name "*.pyc" -delete
    find "$LAYER_DIR" -name "*.pyo" -delete
    find "$LAYER_DIR" -name "*.pyd" -delete
    find "$LAYER_DIR" -name "*.egg-info" | xargs rm -rf
    
    # Remove unnecessary numpy files
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/numpy/doc"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/numpy/tests"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/numpy/random/tests"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/numpy/core/tests"
    
    # Remove unnecessary pandas files
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/pandas/tests"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/pandas/_libs/tslibs/tests"
    
    # Remove unnecessary scikit-learn files
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/sklearn/datasets/tests"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/sklearn/tests"
    rm -rf "$LAYER_DIR/$PYTHON_VERSION/sklearn/utils/tests"
    
    # Create layer zip
    echo "Creating layer zip archive..."
    cd "$LAYER_DIR"
    rm -f "$LAYER_ZIP"
    zip -rq "$LAYER_ZIP" . || {
        echo "Failed to create layer zip"
        exit 1
    }
    cd - > /dev/null
    
    # Publish or update the layer
    echo "Publishing/Updating Lambda Layer..."
    LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name "$LAYER_NAME" \
        --description "Dependencies for Titanic ML Lambda" \
        --license-info "MIT" \
        --zip-file "fileb://$LAYER_ZIP" \
        --compatible-runtimes "$PYTHON_VERSION" \
        --query 'LayerVersionArn' \
        --output text)
        
    if [ $? -ne 0 ]; then
        echo "Failed to publish layer"
        exit 1
    fi
    
    echo "Layer published: $LAYER_ARN"
    
    # Create Lambda function package (just the code, no deps)
    echo "Creating Lambda function package..."
    rm -f "$FUNCTION_ZIP"
    cd "$SCRIPT_DIR"
    zip -q "$FUNCTION_ZIP" train_titanic_lambda.py
    
    echo "Exporting LAYER_ARN for Terraform..."
    export TF_VAR_layer_arn="$LAYER_ARN"

    # Initialize and apply Terraform
    echo "Initializing Terraform..."
    terraform init -input=false || {
        echo "Terraform initialization failed"
        exit 1
    }

    # Validate required environment variables
    if [ -z "${AWS_S3_BUCKET:-}" ]; then
        echo "Error: AWS_S3_BUCKET is not set"
        exit 1
    fi

    echo "Applying Terraform configuration..."
    terraform apply -auto-approve \
        -var="s3_bucket=${AWS_S3_BUCKET}" \
        -var="aws_region=${AWS_DEFAULT_REGION:-eu-central-1}" \
        -var="environment=${ENVIRONMENT:-dev}" || {
        echo "Terraform apply failed"
        exit 1
    }

    echo "Deployment completed successfully"
}

main "$@"