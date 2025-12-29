from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from ...roles import Role

User = get_user_model()


@dataclass(frozen=True)
class TestUserSpec:
    role: Role
    username: str
    group_name: str | None  # None for customers (they aren't grouped)


class Command(BaseCommand):
    help = "Create local test users for each role and print credentials"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset passwords (and demo flags) for existing test users.",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Use a single password for all test users (overrides random).",
        )
        parser.add_argument(
            "--no-print",
            action="store_true",
            help="Do not print credentials (useful for CI).",
        )

    def handle(self, *args, **options):
        reset: bool = options["reset"]
        shared_password: str | None = options["password"]
        no_print: bool = options["no_print"]

        specs: list[tuple[str, str, str]] = [
            TestUserSpec(Role.MANAGER, "alexisrog", Role.MANAGER.label),
            TestUserSpec(Role.DELIVERY_CREW, "brendagiz", Role.DELIVERY_CREW.label),
            TestUserSpec(Role.CUSTOMER, "amyccala", None),
        ]

        results: list[tuple[str, str, str]] = []

        with transaction.atomic():
            for spec in specs:
                password = shared_password or secrets.token_urlsafe(12)

                user, created = User.objects.get_or_create(
                    username=spec.username,
                    defaults={
                        "email": f"{spec.username}@example.com",
                    },
                )

                # If user existed and we are not resetting, keep existing password.
                if created or reset:
                    user.set_password(password)

                # Ensure these are "real" (non-demo) accounts
                update_fields = []
                if hasattr(user, "is_demo"):
                    if getattr(user, "is_demo", False) is not False:
                        user.is_demo = False
                        update_fields.append("is_demo")
                if hasattr(user, "demo_expires_at"):
                    if getattr(user, "demo_expires_at", None) is not None:
                        user.demo_expires_at = None
                        update_fields.append("demo_expires_at")

                # Save if needed
                if created or reset or update_fields:
                    user.save(update_fields=update_fields or None)

                # Group assignment
                if spec.group_name:
                    group, _ = Group.objects.get_or_create(name=spec.group_name)
                    user.groups.add(group)

                results.append(
                    (
                        spec.role.value,
                        spec.username,
                        password if (created or reset) else "unchanged",
                    )
                )

        if no_print:
            self.stdout.write(self.style.SUCCESS("Test users created/updated."))
            return

        self.stdout.write(self.style.SUCCESS("Created/updated test users:\n"))
        self._print_table(results)
        self.stdout.write(
            "\nUse these credentials to obtain JWTs at:\n"
            "    POST /api/v1/auth/jwt/create"
        )

    def _print_table(self, rows: Iterable[tuple[str, str, str]]) -> None:
        # Simple aligned output without external deps
        headers = ("Role", "Username", "Password")
        rows = list(rows)
        col_widths = [
            max(len(headers[0]), *(len(r[0]) for r in rows)),
            max(len(headers[1]), *(len(r[1]) for r in rows)),
            max(len(headers[2]), *(len(r[2]) for r in rows)),
        ]

        def fmt(row):
            return (
                row[0].ljust(col_widths[0])
                + "  "
                + row[1].ljust(col_widths[1])
                + "  "
                + row[2].ljust(col_widths[2])
            )

        self.stdout.write(fmt(headers))
        self.stdout.write(fmt(tuple("-" * w for w in col_widths)))
        for r in rows:
            self.stdout.write(fmt(r))
