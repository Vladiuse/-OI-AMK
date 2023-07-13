from rest_framework import serializers
from .models import SiteImage, ActualUserList


class UserSiteSerializer(serializers.ModelSerializer):
    images = serializers.HyperlinkedIdentityField(
        view_name='checker_2:image-list',
        lookup_url_kwarg='domain_id',
    )

    class Meta:
        model = ActualUserList
        fields = '__all__'


class SiteImageActionSerializer(serializers.ModelSerializer):
    load_orig = serializers.HyperlinkedIdentityField(
        view_name='checker_2:image-load-orig',
        lookup_url_kwarg='image_id',
    )
    make_thumb = serializers.HyperlinkedIdentityField(
        view_name='checker_2:image-make-thumb',
        lookup_url_kwarg='image_id',
    )
    load_make_thumb = serializers.HyperlinkedIdentityField(
        view_name='checker_2:load-make-thumb',
        lookup_url_kwarg='image_id',
    )

    class Meta:
        model = SiteImage
        fields = ['load_orig', 'make_thumb', 'load_make_thumb']


class SiteImagesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='checker_2:image-detail',
        lookup_url_kwarg='image_id',
    )
    actions = SiteImageActionSerializer(
        source='*',
        read_only=True,
    )
    orig_img_params = serializers.ReadOnlyField()
    class Meta:
        model = SiteImage
        fields = '__all__'
        extra_kwargs = {
            'orig_img': {'read_only': True},
            'thumb_img': {'read_only': True},
            'domain': {'read_only': True},
        }