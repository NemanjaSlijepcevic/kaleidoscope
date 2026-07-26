class GenerateOnSaveAndDemand:
    """Cache-file strategy combining imagekit's two built-ins.

    imagekit ships `Optimistic` (generate when the source is saved, never check
    again) and `JustInTime` (generate whenever the file is needed). Neither is
    right on its own here:

    - Optimistic alone means any derived file that was never generated — a
      backfill that skipped an image, a processor change, a wiped cache volume —
      is a permanent 404 with no way to recover except re-running
      `manage.py generateimages`.
    - JustInTime alone means a cold cache is paid for inside page requests,
      which is what made the gallery unusable.

    Generating on save keeps the cache warm in the normal case, so page requests
    do no work; keeping the existence check means a gap in the cache repairs
    itself on first access instead of showing a broken image forever.
    """

    def on_source_saved(self, file):
        file.generate()

    def on_existence_required(self, file):
        file.generate()

    def on_content_required(self, file):
        file.generate()
