import argparse
import sys
import os

from collector_bot import CollectorBot

def read_token(token_filename: str) -> str:
    with open(token_filename, 'r') as token_file:
        return token_file.readline().strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', dest='token_path', action='store',
                        required=True,
                        help='path to text file with token string')
    args = parser.parse_args()
    token = read_token(args.token_path)
    print(token)

    CollectorBot(token).start()