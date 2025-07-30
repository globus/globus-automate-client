def main():
    import sys

    msg = """
    `globus-automate-client` is end-of-life.

    Please use the Globus SDK and Globus CLI as replacements.
    For more information, reference the migration guide here: 
    https://globus-automate-client.readthedocs.io/en/latest/migration.html
    """

    print(msg, file=sys.stderr)
    sys.exit(1)

main()
