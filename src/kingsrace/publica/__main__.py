"""python -m kingsrace.publica {dados <página> | build | serve [porta]}

- dados <página>: grava site/dados/<página>/ a partir das saídas do DVC (etapa site_<página>);
- build: monta _site/ (templates + estático + dados);
- serve: build e prévia em http://localhost:<porta> (padrão 8000).
"""

import functools
import http.server
import importlib
import sys

from kingsrace.publica import build


def main(args: list[str]) -> None:
    if not args:
        raise SystemExit(__doc__)
    if args[0] == "dados":
        modulo = args[1].replace("-", "_")
        importlib.import_module(f"kingsrace.publica.{modulo}").executa()
    elif args[0] == "build":
        for p in build.monta():
            print(p.relative_to(build.SAIDA))
    elif args[0] == "serve":
        build.monta()
        porta = int(args[1]) if len(args) > 1 else 8000
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=build.SAIDA)
        print(f"prévia em http://localhost:{porta}/ (Ctrl+C para sair)")
        http.server.ThreadingHTTPServer(("127.0.0.1", porta), handler).serve_forever()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
