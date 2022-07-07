#!/usr/bin/env python3

"""Точка входа 2.1 этапа - обогащение data frame."""

import os
import sys

from data_preparator.overseer import oversee
from dotenv import load_dotenv

load_dotenv()


def main():
    """Запуск надзирателя."""
    sys.stdout.write('>>>>> Overseer of 2.0 module has started his work <<<<<\n')
    oversee(time_delay=os.environ.get('OVERSEER_TIME_DELAY'))


if __name__ == '__main__':
    main()
