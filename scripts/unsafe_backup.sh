#!/bin/bash
# Insecure backup script for ShellCheck demos
BACKUP_DIR=/tmp/backups
TARGET=$1
AWS_SECRET=AKIAEXAMPLE123456

mkdir -p $BACKUP_DIR
cp $TARGET $BACKUP_DIR/
chmod 777 $BACKUP_DIR/$TARGET
rm -rf /tmp/*

