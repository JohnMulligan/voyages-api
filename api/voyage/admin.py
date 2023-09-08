from django.contrib import admin
import nested_admin
from voyage.models import *
from past.models import *
from document.models import *
from past.admin import EnslavedInRelationInline,EnslaverInRelationInline
from common.models import *
# 
# # 
# # 
class VoyageCrewInline(nested_admin.NestedStackedInline):
	model=VoyageCrew
	max_num=1
	classes = ['collapse']
	fields = [
		'crew_voyage_outset',
		'crew_died_complete_voyage'
	]

class VoyageDatesInline(nested_admin.NestedStackedInline):
	model = VoyageDates
	max_num=1
	classes = ['collapse']
	autocomplete_fields = [
		'voyage_began_sparsedate',
		'slave_purchase_began_sparsedate',
		'vessel_left_port_sparsedate',
		'first_dis_of_slaves_sparsedate',
		'date_departed_africa_sparsedate',
		'arrival_at_second_place_landing_sparsedate',
		'third_dis_of_slaves_sparsedate',
		'departure_last_place_of_landing_sparsedate',
		'voyage_completed_sparsedate',
		'imp_voyage_began_sparsedate',
		'imp_departed_africa_sparsedate',
		'imp_arrival_at_port_of_dis_sparsedate'
	]

# 	inlines=SparseDateInline
	
	
	exclude = [
# 		'voyage_began_sparsedate',
# 		'slave_purchase_began_sparsedate',
# 		'vessel_left_port_sparsedate',
# 		'first_dis_of_slaves_sparsedate',
# 		'date_departed_africa_sparsedate',
# 		'arrival_at_second_place_landing_sparsedate',
# 		'third_dis_of_slaves_sparsedate',
# 		'departure_last_place_of_landing_sparsedate',
# 		'voyage_completed_sparsedate',
# 		'imp_voyage_began_sparsedate',
# 		'imp_departed_africa_sparsedate',
# 		'imp_arrival_at_port_of_dis_sparsedate',
# 		'imp_length_home_to_disembark',
# 		'imp_length_leaving_africa_to_disembark',
		'voyage_began',
		'slave_purchase_began',
		'vessel_left_port',
		'first_dis_of_slaves',
		'date_departed_africa',
		'arrival_at_second_place_landing',
		'third_dis_of_slaves',
		'departure_last_place_of_landing',
		'voyage_completed',
		'imp_voyage_began',
		'imp_departed_africa',
		'imp_arrival_at_port_of_dis',
	]
	verbose_name_plural="Voyage Dates"

class PlaceAdmin(nested_admin.NestedModelAdmin):
	model=Place
	readonly_fields=[
		'geo_location'
	]
	search_fields=['place']

class RegionAdmin(nested_admin.NestedModelAdmin):
	model=Region
	readonly_fields=[
		'geo_location'
	]
	search_fields=['region']

class BroadRegionAdmin(nested_admin.NestedModelAdmin):
	model=BroadRegion
	readonly_fields=[
		'geo_location'
	]
	search_fields=['broad_region']





# # 
class VoyageSlavesNumbersInline(nested_admin.NestedStackedInline):
	model=VoyageSlavesNumbers

	classes = ['collapse']
	max_num=1
# 
# class ParticularOutcomeAdmin(nested_admin.NestedModelAdmin):
# 	list_display = ('name','value')
# 	list_display_links = ('name',)
# 	model=ParticularOutcome
# 	search_fields=['name']
# 	classes = ['collapse']
# 
# class SlavesOutcomeAdmin(nested_admin.NestedModelAdmin):
# 	list_display = ('name','value')
# 	list_display_links = ('name',)
# 	model=SlavesOutcome
# 	search_fields=['name']
# 	classes = ['collapse']
# 	
# class VesselCapturedOutcomeAdmin(nested_admin.NestedModelAdmin):
# 	list_display = ('name','value')
# 	list_display_links = ('name',)
# 	model=VesselCapturedOutcome
# 	search_fields=['name']
# 	classes = ['collapse']
# 
# class OwnerOutcomeAdmin(nested_admin.NestedModelAdmin):
# 	list_display = ('name','value')
# 	list_display_links = ('name',)
# 	model=OwnerOutcome
# 	search_fields=['name']
# 	classes = ['collapse']
# 
# class ResistanceAdmin(nested_admin.NestedModelAdmin):
# 	list_display = ('name','value')
# 	list_display_links = ('name',)
# 	model=Resistance
# 	search_fields=['name']
# 	classes = ['collapse']
# # 
# # ##Autocomplete won't work on this
# # ##Until we update the voyages table to explicitly point at outcomes
# # ##Which I'm still unclear about why it wasn't done that way
# # ##But the number of selections on the outcome table is small enough
# # ##That we don't hit any performance issues here
# # ##So it can stay for now
# # ##Until I figure out what's going to break when I migrate that.
# # ##It is worth saying that I think it's currently broken
# # ##Insofar as you can apply more than one outcome entry to each voyage
# # ##But it doesn't appear that this has ever been done
# # ##which on this admin page results in multiple possible outcome fields being allowed
class VoyageOutcomeInline(nested_admin.NestedStackedInline):
	max_num = 0
	classes = ['collapse']
	model=VoyageOutcome
# 
# class NationalityAdmin(nested_admin.NestedModelAdmin):
# 	search_fields=['name']
# 	model=Nationality
# 
# class TonTypeAdmin(nested_admin.NestedModelAdmin):
# 	search_fields=['name']
# 	model=TonType
# 
# class RigOfVesselAdmin(nested_admin.NestedModelAdmin):
# 	model=RigOfVessel
# 	search_fields=['name']

# 
class VoyageShipInline(nested_admin.NestedStackedInline):
	model = VoyageShip
	max_num = 1
# 	autocomplete_fields=[
# 		'nationality_ship',
# 		'ton_type',
# 		'rig_of_vessel',
# 		'vessel_construction_place',
# 		'vessel_construction_region',
# 		'registered_place',
# 		'registered_region',
# 		'imputed_nationality'
# 	]
	classes = ['collapse']
# 
class VoyageItineraryInline(nested_admin.NestedStackedInline):
	model = VoyageItinerary
	max_num = 1
	autocomplete_fields=[
		'imp_broad_region_voyage_begin',
		'port_of_departure',
		'int_first_port_emb',
		'int_third_port_dis',
		'int_fourth_port_dis',
		'int_third_place_region_slave_landing',
		'int_fourth_place_region_slave_landing',
		'int_second_port_emb',
		'int_first_region_purchase_slaves',
		'int_second_region_purchase_slaves',
		'int_first_port_dis',
		'int_second_port_dis',
		'int_first_region_slave_landing',
		'imp_principal_region_slave_dis',
		'int_second_place_region_slave_landing',
		'first_place_slave_purchase',
		'second_place_slave_purchase',
		'third_place_slave_purchase',
		'first_region_slave_emb',
		'second_region_slave_emb',
		'third_region_slave_emb',
		'first_landing_place',
		'second_landing_place',
		'third_landing_place',
		'first_landing_region',
		'second_landing_region',
		'third_landing_region',
		'place_voyage_ended',
		'imp_port_voyage_begin',
		'principal_place_of_slave_purchase',
		'imp_principal_place_of_slave_purchase',
		'imp_principal_region_of_slave_purchase',
		'imp_broad_region_of_slave_purchase',
		'principal_port_of_slave_dis',
		'imp_principal_port_slave_dis',
		'imp_broad_region_slave_dis'
	]
	exclude= [
		'port_of_call_before_atl_crossing',
		'number_of_ports_of_call',
		'region_of_return',
		'broad_region_of_return',
		'imp_region_voyage_begin',
		'imp_broad_region_voyage_begin'
		
	]
	classes = ['collapse']
# 

# class VoyageSourcesConnectionInline(nested_admin.NestedStackedInline):
# 	model=VoyageSourcesConnection
# 	autocomplete_fields=['source']
# 	fields=[
# 		'source',
# 		'text_ref'
# 	]
# 	classes = ['collapse']
# 	extra=0
# # 
class VoyageSourcesAdmin(nested_admin.NestedModelAdmin):
	search_fields=['full_ref','short_ref']
	list_display=['short_ref','full_ref']
	model=VoyageSources
# 
class VoyageOutcomeInline(nested_admin.NestedStackedInline):
	model=VoyageOutcome
	extra=0
# 	autocomplete_fields=[
# 		'particular_outcome',
# 		'resistance',
# 		'outcome_slaves',
# 		'vessel_captured_outcome',
# 		'outcome_owner'
# 	]
	classes = ['collapse']

class VoyageZoteroConnectionInline(nested_admin.NestedStackedInline):
	model=ZoteroVoyageConnection
	autocomplete_fields=['zotero_source']
# 	fields=['__all__',]
	extra=0
	classes=['collapse']
	
class EnslavedInRelationInline(nested_admin.NestedStackedInline):
	model=EnslavedInRelation
	autocomplete_fields=['enslaved']
	readonly_fields=['relation']
	classes = ['collapse']
	sortable_field_name='enslaved'
	extra=0

class EnslaverInRelationInline(nested_admin.NestedStackedInline):
	model=EnslaverInRelation
	autocomplete_fields=[
		'enslaver_alias'
	]
	sortable_field_name='enslaver_alias'
	readonly_fields=['relation']
	classes = ['collapse']
	exclude=['order']
	extra=0



class EnslavementRelationInline(nested_admin.NestedStackedInline):
	model = EnslavementRelation
	inlines=[
		EnslavedInRelationInline,
		EnslaverInRelationInline
	]
	sortable_field_name='voyage'
	extra=0
	exclude=['source','place','text_ref','unnamed_enslaved_count','date','amount','is_from_voyages']

class VoyageAdmin(nested_admin.NestedModelAdmin):
	inlines=(
		VoyageDatesInline,
		VoyageItineraryInline,
# 		VoyageSourcesConnectionInline,
		VoyageZoteroConnectionInline,
# 		EnslaverAliasConnectionInline,
		EnslavementRelationInline,
		VoyageCrewInline,
		VoyageOutcomeInline,
		VoyageShipInline,
		VoyageSlavesNumbersInline,
	)
	fields=['voyage_id','dataset','voyage_in_cd_rom']
	list_display=('voyage_id',)
	search_fields=('voyage_id',)
	classes = ['collapse']
	model=Voyage
# 
# 
admin.site.register(Voyage, VoyageAdmin)
# admin.site.register(VoyageDates)
admin.site.register(Place,PlaceAdmin)
admin.site.register(Region,RegionAdmin)
admin.site.register(BroadRegion,BroadRegionAdmin)
admin.site.register(VoyageSources, VoyageSourcesAdmin)
# admin.site.register(ParticularOutcome, ParticularOutcomeAdmin)
# admin.site.register(SlavesOutcome, SlavesOutcomeAdmin)
# admin.site.register(VesselCapturedOutcome, VesselCapturedOutcomeAdmin)
# admin.site.register(OwnerOutcome, OwnerOutcomeAdmin)
# admin.site.register(Resistance, ResistanceAdmin)
# admin.site.register(Nationality, NationalityAdmin)
# admin.site.register(TonType, TonTypeAdmin)
admin.site.register(RigOfVessel)
