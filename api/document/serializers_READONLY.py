from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField,Field
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from voyages3.localsettings import STATIC_URL,OPEN_API_BASE_API
from common.static.Source_options import Source_options

class SourceTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourceType
		fields='__all__'

# class TranscriptionSerializer(Serializers.ModelSerializer):
# 	class Meta:
# 		model=Transcription
# 		fields='__all__'

class DocSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=DocSparseDate
		fields='__all__'

class SourceVoyageSerializer(serializers.ModelSerializer):
	class Meta:
		model=Voyage
		fields='__all__'

class SourceVoyageConnectionSerializer(serializers.ModelSerializer):
	voyage=SourceVoyageSerializer(many=False)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class SourceEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields='__all__'
	def create(self, validated_data):
		try:
			return Enslaved.objects.get(enslaved_id=validated_data['enslaved_id'])
		except ObjectDoesNotExist:
			return super(SourceEnslavedSerializer, self).create(validated_data)

class SourceEnslavedConnectionSerializer(serializers.ModelSerializer):
	enslaved=SourceEnslavedSerializer(many=False,read_only=True)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

class SourceEnslavementRelationSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class SourceEnslavementRelationConnectionSerializer(serializers.ModelSerializer):
	enslavement_relation=SourceEnslavementRelationSerializer(many=False)
	class Meta:
		model=SourceEnslavementRelationConnection
		fields='__all__'

class SourceEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class SourceEnslaverConnectionSerializer(serializers.ModelSerializer):
	enslaver=SourceEnslaverIdentitySerializer(many=False,read_only=True)
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'

class PageSerializer(serializers.ModelSerializer):
	class Meta:
		model=Page
		fields='__all__'			

class SourcePageConnectionSerializer(serializers.ModelSerializer):
	page=PageSerializer(many=False,read_only=True)
	class Meta:
		model=SourcePageConnection
		fields='__all__'

class ShortRefSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'

class ShortRefSerializer(serializers.ModelSerializer):
	short_ref_sources=ShortRefSourceSerializer(many=True,read_only=True)
	class Meta:
		model=ShortRef
		fields='__all__'

class SourceShortRefSerializer(serializers.ModelSerializer):
	class Meta:
		model=ShortRef
		fields=['id','name']

class SourceSerializer(serializers.ModelSerializer):
	source_type=SourceTypeSerializer(many=False)
	page_connections=SourcePageConnectionSerializer(many=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True)
	source_enslavement_relation_connections=SourceEnslavementRelationConnectionSerializer(many=True)
	short_ref=SourceShortRefSerializer(many=False,allow_null=False)
	date=DocSparseDateSerializer(many=False,allow_null=True)
	iiif_manifest_url=SerializerMethodField()
	class Meta:
		model=Source
		fields='__all__'
	def get_iiif_manifest_url(self,obj):
		if obj.has_published_manifest and obj.zotero_group_id and obj.zotero_item_id is not None:
			return(f'{OPEN_API_BASE_API}{STATIC_URL}iiif_manifests/{obj.zotero_group_id}__{obj.zotero_item_id}.json')
		else:
			return None


############ REQUEST FIILTER OBJECTS
class AnyField(Field):
	def to_representation(self, value):
		return value
	def to_internal_value(self, data):
		return data

class SourceFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw"])
	varName=serializers.ChoiceField(choices=[k for k in Source_options])
	searchTerm=AnyField()


@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Filtered search for docs with manifests',
            summary='Filtered search for docs with manifests',
            description='Here, we search for documents a) whose titles containing a substring like "creole" and b) have manifests (there is only one result, from the Texas/OMNO data).',
            value={
			  "filter": [
				{
				  "varName": "has_published_manifest",
				  "op": "exact",
				  "searchTerm": True
				},
				{
				  "varName": "title",
				  "op": "icontains",
				  "searchTerm": "creole"
				}
			  ]
			},
			request_only=True,
			response_only=False
        ),
		OpenApiExample(
            'Exact match on a nested field',
            summary='Exact match on a nested field',
            description='Here, we search for an exact match on the short valuefield.',
            value={
            	"filter":[
					{
						"varName":"short_ref__name",
						"op":"in",
						"searchTerm":["1713Poll"]
					}
            	]
			},
			request_only=True,
			response_only=False
        )
    ]
)
class SourceRequestSerializer(serializers.Serializer):
	filter=SourceFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)
	order_by=serializers.ListField(child=serializers.CharField(allow_null=True),required=False,allow_null=True)
	page=serializers.IntegerField(required=False,allow_null=True)
	page_size=serializers.IntegerField(required=False,allow_null=True)
	
class SourceListResponseSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=SourceSerializer(many=True,read_only=True)
