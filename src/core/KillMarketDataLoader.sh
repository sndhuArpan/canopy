#!/bin/sh

ps aux | grep -ie RunM | awk '{print $2}' | xargs kill -9