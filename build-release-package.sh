#!/bin/bash

LAMBDA_BUILD_DIR="temp-package-build"
LAMBDA_ZIP_NAME="dynatrace-aws-log-forwarder-lambda.zip"

PACKAGE_BUILD_DIR="dynatrace-aws-log-forwarder"
PACKAGE_ZIP_NAME="dynatrace-aws-log-forwarder.zip"

set -ex

rm -f $LAMBDA_ZIP_NAME
rm -rf $LAMBDA_BUILD_DIR


# PREPARE LAMBDA ZIP

mkdir $LAMBDA_BUILD_DIR
sh version.sh

# add lambda source
cp -r src/* $LAMBDA_BUILD_DIR

# add dependencies
pip3 install -r src/requirements.txt --target $LAMBDA_BUILD_DIR

# create lambda ZIP
cd $LAMBDA_BUILD_DIR
zip -r ../$LAMBDA_ZIP_NAME *
cd ..
rm -rf $LAMBDA_BUILD_DIR


# PREPARE WHOLE PACKAGE ZIP

mkdir $PACKAGE_BUILD_DIR

cp README.md dynatrace-aws-logs.sh $LAMBDA_ZIP_NAME dynatrace-aws-log-forwarder-template.yaml $PACKAGE_BUILD_DIR
zip $PACKAGE_ZIP_NAME $PACKAGE_BUILD_DIR/*

rm -rf $PACKAGE_BUILD_DIR
