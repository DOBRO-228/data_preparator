#!/usr/bin/env python3

"""Точка входа 2.1 этапа - обогащение data frame."""

import os
import sys

from dotenv import load_dotenv

from .overseer import oversee

load_dotenv()


def main():
    """Запуск надзирателя."""
    sys.stdout.write('>>>>> Overseer of 2.0 module has started his work <<<<<\n')
    oversee(time_delay=os.environ.get('OVERSEER_TIME_DELAY'))


if __name__ == '__main__':
    main()
