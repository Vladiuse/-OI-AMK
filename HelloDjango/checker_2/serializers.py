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
    is_over_size = serializers.ReadOnlyField()
    class Meta:
        model = SiteImage
        fields = '__all__'
        extra_kwargs = {
            'orig_img': {'read_only': True},
            'thumb_img': {'read_only': True},
            'domain': {'read_only': True},
        }

class SiteImageCropSerializer(serializers.ModelSerializer):
    width = serializers.IntegerField()
    height  = serializers.IntegerField()

    class Meta:
        model = SiteImage
        fields = ['pk', 'width', 'height']

li = [{'id': 13931, 'width': 430, 'height': 465}, {'id': 1406, 'width': 40, 'height': 40}, {'id': 1408, 'width': 40, 'height': 40}, {'id': 1409, 'width': 40, 'height': 41}, {'id': 1410, 'width': 40, 'height': 40}, {'id': 1412, 'width': 40, 'height': 40}, {'id': 1413, 'width': 350, 'height': 467}, {'id': 1415, 'width': 40, 'height': 40}, {'id': 1414, 'width': 40, 'height': 40}, {'id': 1416, 'width': 40, 'height': 40}, {'id': 1418, 'width': 40, 'height': 40}, {'id': 1419, 'width': 40, 'height': 40}, {'id': 1420, 'width': 40, 'height': 40}, {'id': 1421, 'width': 40, 'height': 40}, {'id': 1422, 'width': 40, 'height': 40}, {'id': 1423, 'width': 40, 'height': 40}, {'id': 1424, 'width': 40, 'height': 42}, {'id': 1425, 'width': 40, 'height': 40}, {'id': 1427, 'width': 40, 'height': 40}, {'id': 1428, 'width': 350, 'height': 467}, {'id': 1429, 'width': 40, 'height': 40}]
