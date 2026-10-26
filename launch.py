#!/usr/bin/env python3
"""Serve AssetWorkshop's standalone preview; no game or browser startup required."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--localhost', action='store_true',
                        help='Compatibility flag; this server always binds localhost')
    parser.add_argument('--no-open', action='store_true',
                        help='Compatibility flag; this server never opens a browser')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'Preview: http://127.0.0.1:{args.port}/tools/asset-pipeline/preview/',
              flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
