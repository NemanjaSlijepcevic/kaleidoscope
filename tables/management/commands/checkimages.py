from django.core.management.base import BaseCommand

from tables.models import Image


class Command(BaseCommand):
    help = (
        "Report which images cannot produce their derived files, and why. "
        "`generateimages` swallows per-image errors into its output and still "
        "exits 0, so a partial backfill is easy to miss; this fails loudly and "
        "names the rows to look at."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repair",
            action="store_true",
            help="Regenerate the derived files for any image reported as broken.",
        )

    def handle(self, *args, **options):
        broken = []
        missing_source = []
        ok = 0

        for image in Image.objects.all().iterator():
            if not image.image:
                missing_source.append((image, "no file recorded on the row"))
                continue
            try:
                if not image.image.storage.exists(image.image.name):
                    missing_source.append((image, f"source gone: {image.image.name}"))
                    continue
            except Exception as exc:
                missing_source.append((image, f"source unreadable: {exc}"))
                continue

            for spec in ("thumbnail", "watermarked"):
                try:
                    getattr(image, spec).generate()
                except Exception as exc:
                    broken.append((image, spec, f"{type(exc).__name__}: {exc}"))
                    break
            else:
                ok += 1

        for image, reason in missing_source:
            self.stdout.write(self.style.WARNING(f"  #{image.pk} {image.title!r}: {reason}"))
        for image, spec, reason in broken:
            self.stdout.write(self.style.ERROR(f"  #{image.pk} {image.title!r} [{spec}]: {reason}"))

        total = Image.objects.count()
        self.stdout.write(
            f"\n{ok}/{total} images have both derived files; "
            f"{len(broken)} failed to render, {len(missing_source)} have no usable source."
        )

        if options["repair"] and broken:
            self.stdout.write("\nRetrying the failures...")
            repaired = 0
            for image, spec, _reason in broken:
                try:
                    getattr(image, spec).generate()
                    repaired += 1
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"  #{image.pk} still failing: {exc}"))
            self.stdout.write(f"repaired {repaired}/{len(broken)}")

        if missing_source:
            self.stdout.write(
                "\nRows with no usable source cannot be fixed here — either the media "
                "volume is not mounted where it was when they were uploaded, or the "
                "files were deleted. Re-upload them or remove the rows."
            )
