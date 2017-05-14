
import logging
from fortunes.serve import main

if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
