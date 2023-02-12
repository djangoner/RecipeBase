from thumbnails.backends.metadata import DatabaseBackend, ImageMeta
from thumbnails.models import Source, ThumbnailMeta


class ThumbnailDBBackend(DatabaseBackend):
    def get_or_create_source(self, name):
        s, _ = Source.objects.get_or_create(name=name)
        return s

    def add_thumbnail(self, source_name, size, name):
        source = self.get_or_create_source(source_name)
        meta, _ = ThumbnailMeta.objects.get_or_create(
            source=source, size=size, name=name
        )
        return ImageMeta(source_name, meta.name, meta.size)
