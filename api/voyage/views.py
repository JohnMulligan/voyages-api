from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from rest_framework.pagination import PageNumberPagination
from collections import Counter
import urllib
import json
import requests
import time
from .models import *
import pprint
from rest_framework import filters
from common.reqs import *
# from common.serializers import autocompleterequestserializer, autocompleteresponseserializer,crosstabresponseserializer,crosstabrequestserializer
from geo.common import GeoTreeFilter
from geo.serializers_READONLY import LocationSerializerDeep
import collections
import gc
from .serializers import *
from .serializers_READONLY import *
from rest_framework import serializers
from voyages3.localsettings import *
from drf_yasg.utils import swagger_auto_schema
import re
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from common.static.Voyage_options import Voyage_options

class VoyageList(generics.GenericAPIView):
	permission_classes=[IsAuthenticated]
	authentication_classes=[TokenAuthentication]
	serializer_class=VoyageSerializer
	@extend_schema(
		description="\
		This endpoint returns a list of nested objects, each of which contains all the available information on individual voyages.\n\
		Voyages are the legacy natural unit of the project. They are useful because they gather together:\n\
			1. Numbers of people and demographic data\n\
			2. Geographic itinerary data\n\
			3. Important dates\n\
			4. Named individuals\n\
			5. Documentary sources\n\
			6. Data on the vessel\n\
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.\n\
		",
		request=VoyageListRequestSerializer
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		#VALIDATE THE REQUEST
		
		serialized_req = VoyageListRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
			
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=True
		)
		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=VoyageListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)

class VoyageAggregations(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="\n\
		The aggregations endpoints helps us to peek at numerical fields in the same way that autcomplete endpoints help us to get a sense of what the available text values are on a field.\n\
		So if we want to, for instance, allow a user to search on voyages by year, we might want to give them a rangeslider component. In order to make that rangeslider component, you'd have to know the minimum and maximum years during which voyages sailed -- you would also need to know, of course, whether you were searching for the minimum and maximum of years of departure, embarkation, disembarkation, return, etc.\n\
		Also, as with the other new endpoints we are rolling out in January 2024, you can run a filter before you query for min/max on variables. So if you've already searched for voyages arriving in Cuba, for instance, you can ask for the min and max years of disembarkation in order to make a rangeslider dynamically tailored to that search.\n\
		Note to maintainer(s): This endpoint was made with rangesliders in mind, so we are only exposing min & max for now. In the future, it could be very useful to have median, mean, or plug into the stats engine for a line or bar chart to create some highly interactive filtering.\n\
		",
		request=VoyageFieldAggregationRequestSerializer,
		responses=VoyageFieldAggregationResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE AGGREGATIONS+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageFieldAggregationRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
		)
		
		#RUN THE AGGREGATIONS
		aggregation_field=request.data.get('varName')
		output_dict,errormessages=get_fieldstats(queryset,aggregation_field,Voyage_options)
		
		print("++++++++",output_dict)
		
		#VALIDATE THE RESPONSE
		serialized_resp=VoyageFieldAggregationResponseSerializer(data=output_dict)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class VoyageCrossTabs(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="Paginated crosstabs endpoint, with Pandas as the back-end.",
		request=VoyageCrossTabRequestSerializer,
		responses=VoyageCrossTabResponseSerializer,
		examples=[	
			OpenApiExample(
				'Paginated request for binned years & embarkation geo vars',
				summary='Multi-level, paginated, 20-year bins',
				description='Here, we request cross-tabs on the geographic locations where enslaved people were embarked in 20-year periods. We also request that our columns be grouped in a multi-level way, from broad region to region and place. The cell value we wish to calculate is the number of people embarked, and we aggregate these as a sum. We are requesting the first 5 rows of these cross-tab results.',
				value={
					"columns":[
						"voyage_itinerary__imp_broad_region_of_slave_purchase__name",
						"voyage_itinerary__imp_principal_region_of_slave_purchase__name",
						"voyage_itinerary__imp_principal_place_of_slave_purchase__name"
					],
					"rows":"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
					"binsize": 20,
					"rows_label":"YEARAM",
					"agg_fn":"sum",
					"value_field":"voyage_slaves_numbers__imp_total_num_slaves_embarked",
					"offset":0,
					"limit":5,
					"filter":[]
				},
				request_only=True,
				response_only=False
			)
		]
	)

	def post(self,request):
		st=time.time()
		print("VOYAGE CROSSTABS+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageCrossTabRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=True
		)
		
		#MAKE THE CROSSTABS REQUEST TO VOYAGES-STATS
		ids=[i[0] for i in queryset.values_list('id')]
		u2=STATS_BASE_URL+'crosstabs/'
		params=dict(request.data)
		stats_req_data=params
		stats_req_data['ids']=ids
		r=requests.post(url=u2,data=json.dumps(stats_req_data),headers={"Content-type":"application/json"})
		
		#VALIDATE THE RESPONSE
		if r.ok:
			serialized_resp=VoyageCrossTabResponseSerializer(data=json.loads(r.text))
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)
# 
# 
# 		
# 		resp=VoyageListResponseSerializer({
# 			'count':total_results_count,
# 			'page':page_num,
# 			'page_size':page_size,
# 			'results':results
# 		}).data
# 		
# 		params=dict(request.data)
# 		queryset=Voyage.objects.all()
# 		queryset,selected_fields,results_count,error_messages=post_req(
# 			queryset,
# 			self,
# 			request,
# 			Voyage_options
# 		)
# 		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			u2=STATS_BASE_URL+'crosstabs/'
			params=dict(request.data)
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})

class VoyageGroupBy(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint is intended for use building line/scatter, bar, and pie charts. It requires a few arguments, which it basically inherits from <a href=\"https://github.com/rice-crc/voyages-api/tree/main/stats\">the back-end flask/pandas service</a> that runs these stats.\n\
		    1. A variable to group on: 'groupby_by'\n\
		        1a. For a scatter plot, you would want this would be a numeric variable\n\
		        1b. For a bar chart, you would want this to be a categorical variable\n\
		    2. An array of variables to aggregate on: 'groupby_cols'\n\. This is always a numeric variable.\n\
		    3. An aggregation function: sum, mean, min, max\n\
		It returns a dictionary whose keys are the supplied variable names, and whose values are equal-length arrays -- in essence, a small, serialized dataframe taken from the pandas back-end.\n\
		",
		request=VoyageGroupByRequestSerializer
	)

	def post(self,request):
		st=time.time()
		print("VOYAGE GROUPBY+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageGroupByRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
		)
		
		#EXTRACT THE VOYAGE IDS AND HAND OFF TO THE STATS FLASK CONTAINER
		ids=[i[0] for i in queryset.values_list('id')]
		u2=STATS_BASE_URL+'groupby/'
		d2=dict(request.data)
		d2['ids']=ids
		
		#NOT QUITE SURE HOW TO VALIDATE THE RESPONSE OF THIS VIA A SERIALIZER
		#BECAUSE YOU HAVE A DICTIONARY WITH > 2 KEYS COMING BACK AT YOU
		#AND ANOTHER GOOD RULE WOULD BE THAT THE ARRAYS ARE ALL EQUAL IN LENGTH
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)

class VoyageDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The dataframes endpoint is mostly for internal use -- building up caches of data in the flask services.\n\
		However, it could be used for csv exports and the like.\n\
		\n\
		Be careful!\n\. It's a resource hog. But more importantly, if you request fields that are not one-to-one relationships with the voyage, you're likely get back extra rows. For instance, requesting captain names will return one row for each captain, not for each voyage.\n\
		\n\
		And finally, the example provided below puts a strict year filter on because unrestricted, it will break your swagger viewer :) \n\
		",
		request=VoyageDataframesRequestSerializer
	)
	def post(self,request):
		print("VOYAGE AGGREGATIONS+++++++\nusername:",request.auth.user)
		st=time.time()
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageDataframesRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=True
		)
		
		queryset=queryset.order_by('id')
		sf=request.data.get('selected_fields')
		output_dicts={}
		vals=list(eval('queryset.values_list("'+'","'.join(sf)+'")'))
		for i in range(len(sf)):
			output_dicts[sf[i]]=[v[i] for v in vals]
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		## DIFFICULT TO VALIDATE THIS WITH A SERIALIZER -- NUMBER OF KEYS AND DATATYPES WITHIN THEM CHANGES DYNAMICALLY ACCORDING TO REQ
		
		return JsonResponse(output_dicts,safe=False)

class VoyageGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint is tricky. In addition to taking a filter object, it also takes a list of geographic value variable names, like 'voyage_itinerary__port_of_departure__value'. \n\
		What it returns is a hierarchical tree of SlaveVoyages geographic data, filtered down to only the values used in those 'geotree valuefields' after applying the filter object.\n\
		So if you were to ask for voyage_itinerary__port_of_departure__value, you would mostly get locations in Europe and the Americas; and if you searched 'voyage_itinerary__imp_principal_region_of_slave_purchase__name', you would principally get places in the Americas and Africa.",
		request=VoyageGeoTreeFilterRequestSerializer,
		responses=LocationSerializerDeep
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE GEO TREE FILTER+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageGeoTreeFilterRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#extract and then peel out the geotree_valuefields
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			reqdict,
			Voyage_options
		)
		
		#THEN GET THE CORRESPONDING GEO VALUES
		for geotree_valuefield in geotree_valuefields:
			geotree_valuefield_stub='__'.join(geotree_valuefield.split('__')[:-1])
			queryset=queryset.select_related(geotree_valuefield_stub)
		vls=[]
		for geotree_valuefield in geotree_valuefields:		
			vls+=[i[0] for i in list(set(queryset.values_list(geotree_valuefield))) if i[0] is not None]
		vls=list(set(vls))
		
		#THEN GET THE GEO OBJECTS BASED ON THAT OPERATION
		filtered_geotree=GeoTreeFilter(spss_vals=vls)
		
		### CAN'T FIGURE OUT HOW TO SERIALIZE THIS...
		
		resp=JsonResponse(filtered_geotree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp

class VoyageCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the voyage). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the voyages list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=VoyageAutoCompleteRequestSerializer,
		responses=VoyageAutoCompleteResponseSerializer,
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageAutoCompleteRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
		)
		
		#RUN THE AUTOCOMPLETE ALGORITHM
		final_vals=autocomplete_req(queryset,request)
		resp=dict(request.data)
		resp['suggested_values']=final_vals
		
		#VALIDATE THE RESPONSE
		serialized_resp=VoyageAutoCompleteResponseSerializer(data=resp)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class VoyageAggRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint provides a collection of multi-valued weighted nodes and splined, weighted edges. The intended use-case is the drawing of a geographic sankey map.",
		request=VoyageAggRoutesRequestSerializer,
		responses=VoyageAggRoutesResponseSerializer,
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE AGGREGATION ROUTES+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageAggRoutesRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		params=dict(request.data)
		zoom_level=params.get('zoom_level')
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=True
		)
		
		#HAND OFF TO THE FLASK CONTAINER
		queryset=queryset.order_by('id')
		zoomlevel=params.get('zoomlevel','region')
		values_list=queryset.values_list('id')
		pks=[v[0] for v in values_list]
		django_query_time=time.time()
		print("Internal Django Response Time:",django_query_time-st,"\n+++++++")
		u2=GEO_NETWORKS_BASE_URL+'network_maps/'
		d2={
			'graphname':zoomlevel,
			'cachename':'voyage_maps',
			'pks':pks
		}
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		
# 		print("--->",r)
# 		print(json.loads(r.text))
		
		#VALIDATE THE RESPONSE
		if r.ok:
			serialized_resp=VoyageAggRoutesResponseSerializer(data=json.loads(r.text))
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

@extend_schema(
		exclude=True
	)
class VoyageCREATE(generics.CreateAPIView):
	'''
	Create Voyage without a pk
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class VoyageRETRIEVE(generics.RetrieveAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class VoyageUPDATE(generics.UpdateAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	
	Previously, the SQL pk ("id") always corresponded to the "voyage_id" field. We will not be enforcing this going forward.
	
	M2M relations will not be writable here EXCEPT in the case of union/"through" tables.
	
	Examples:
	
		1. You CANNOT create an Enslaved (person) record as you traverse voyage_enslavement_relations >> relation_enslaved, but only the EnslavementRelation record that joins them
		2. You CAN create an EnslaverInRelation record as you traverse voyage_enslavement_relations >> relation_enslaver >> enslaver_alias >> enslaver_identity ...
		3. ... but you CANNOT create an EnslaverRole record during that traversal, like voyage_enslavement_relations >> relation_enslaver >> enslaver_role
	
	I have also, for the time, set all itinerary Location foreign keys as read_only.
	
	Godspeed.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class VoyageDESTROY(generics.DestroyAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]


@extend_schema(
		exclude=True
	)
class VoyageStatsOptions(generics.GenericAPIView):
	'''
	Need to make the stats engine's indexed variables transparent to the user
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		u2=STATS_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)
	def options(self,request):
		u2=STATS_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)
