"""nox sessions for attributedict (I-015/I-016)."""

import nox

nox.options.sessions = ["tests"]


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def tests(session):
    session.install("pytest", "hypothesis", ".")
    session.run("pytest", "tests/")


@nox.session
def build(session):
    """Build sdist + abi3 wheel (I-015)."""
    session.install("build")
    session.run("python", "-m", "build")


@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", "src", "tests")


@nox.session
def format(session):
    session.install("ruff")
    session.run("ruff", "format", "--check", "src", "tests")


@nox.session
def typecheck(session):
    session.install("mypy")
    session.run("mypy", "src")


@nox.session
def coverage(session):
    session.install("pytest", "pytest-cov", ".")
    session.run("pytest", "--cov=attributedict", "--cov-report=term-missing", "tests/")


@nox.session
def benchmarks(session):
    session.install(".")
    session.run("python", "benchmarks/bench.py")
