from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

from app import routes, models
import requests
import urllib.request
import xml.etree.ElementTree as ET
from app import db
from app.models import Station, Metar, Taf, Pirep
import click
from datetime import datetime


@app.cli.command()
def loadSTATION():
    """Load Stations."""
    url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=stations&requestType=retrieve&format=xml"

    content = urllib.request.urlopen(url).read()

    root = ET.fromstring(content)
    for station in root.iter('Station'):
        if station.find('station_id') is None:
            print("Skipping")
            continue
        stationId = station.find('station_id').text
        latitude = station.find('latitude').text
        longitude = station.find('longitude').text
        elevation = station.find('elevation_m').text
        site = station.find('site').text
        if station.find('wmo_id') is not None:
            wmo_id = station.find('wmo_id').text
        else:
            wmo_id = None
        if station.find('state') is not None:
            state = station.find('state').text
        else:
            state = None
        country = station.find('country').text
        if station.find('site_type') is None:
            metar = None
            rawinsonde = None
            taf = None
            nexrad = None
            wind_profiler = None
            wfo_office = None
            synops = None
        else:
            for site_type in station.iter('site_type'):
                METAR = site_type.find('METAR')
                TAF = site_type.find('TAF')
                raw = site_type.find('rawinsonde')
                NEXRAD = site_type.find('NEXRAD')
                wind = site_type.find('wind_profiler')
                wfo = site_type.find('WFO_office')
                syn = site_type.find('SYNOPS')
                if METAR is not None:
                    METAR = True
                else:
                    METAR = False
                if TAF is not None:
                    TAF = True
                else:
                    TAF = False
                if raw is not None:
                    raw = True
                else:
                    raw = False
                if NEXRAD is not None:
                    NEXRAD = True
                else:
                    NEXRAD = False
                if wind is not None:
                    wind = True
                else:
                    wind = False
                if wfo is not None:
                    wfo = True
                else:
                    wfo = False
                if syn is not None:
                    syn = True
                else:
                    syn = False

        stationDB = Station.query.filter_by(station_id=stationId).first()
        if stationDB is None:
            stationDB = Station(station_id=stationId, wmo_id=wmo_id, latitude=latitude, longitude=longitude, elevation_m=elevation, site=site, state=state, country=country, metar=METAR, taf=TAF, rawinsonde=raw, nexrad=NEXRAD, wind_profiler=wind, wfo_office=wfo, synops=syn)
            db.session.add(stationDB)
            db.session.commit()
        elif stationDB.station_id==stationId and (stationDB.wmo_id!=wmo_id or stationDB.latitude!=latitude or stationDB.longitude!=longitude or stationDB.elevation_m!=elevation or stationDB.site!=site or stationDB.state!=state or stationDB.country!=country or stationDB.metar!=METAR or stationDB.taf!=TAF or stationDB.rawinsonde!=raw or stationDB.nexrad!=NEXRAD or stationDB.wind_profiler!=wind or stationDB.wfo_office!=wfo or stationDB.synops!=syn):
            print(stationDB.station_id)
            stationDB.wmo_id = wmo_id
            stationDB.latitude = latitude
            stationDB.longitude = longitude
            stationDB.elevation_m = elevation
            stationDB.site = site
            stationDB.state = state
            stationDB.country = country
            stationDB.metar = METAR
            stationDB.taf = TAF
            stationDB.synops = syn
            stationDB.wfo_office = wfo
            stationDB.wind_profiler = wind
            stationDB.nexrad = NEXRAD
            stationDB.rawinsonde = raw
            db.session.commit()

@app.cli.command()
def loadMETAR(): 
    """Load METAR."""
    url = "https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.xml"

    content = urllib.request.urlopen(url).read()

    root = ET.fromstring(content)
    for metar in root.iter('METAR'):
        raw_text = metar.find('raw_text').text
        if metar.find('flight_category') is not None:
            flightCategory = metar.find('flight_category').text
        else:
            flightCategory = None
        stationId = metar.find('station_id').text
        if metar.find('temp_c') is not None:
            temp_c = metar.find('temp_c').text
        else:
            temp_c = None
        observation_time = metar.find('observation_time').text
        if metar.find('latitude') is not None:
            latitude = metar.find('latitude').text
            longitude = metar.find('longitude').text
        else:
            latitude = None
            longitude = None
        if metar.find('dewpoint_c') is not None:
            dewpoint_c = metar.find('dewpoint_c').text
        else:
            dewpoint_c = None
        if metar.find('wind_dir_degrees') is not None:
            wind_dir_degrees = metar.find('wind_dir_degrees').text
        else:
            wind_dir_degrees = None
        if metar.find('wind_speed_kt') is not None:
            wind_speed_kt = metar.find('wind_speed_kt').text
        else:
            wind_speed_kt = None
        if metar.find('wind_gust_kt') is not None:
            wind_gust_kt = metar.find('wind_gust_kt').text
        else:
            wind_gust_kt = None
        if metar.find('visibility_statute_mi') is not None:
            visibility_statute_mi = metar.find('visibility_statute_mi').text
        else:
            visibility_statute_mi = None
        if metar.find('altim_in_hg') is not None:
            altim_in_hg = metar.find('altim_in_hg').text
        else:
            altim_in_hg = None
        if metar.find('sea_level_pressure_mb') is not None:
            sea_level_pressure_mb = metar.find('sea_level_pressure_mb').text
        else:
            sea_level_pressure_mb = None
        if metar.find('wx_string') is not None:
            wx_string = metar.find('wx_string').text
        else:
            wx_string = None
        if metar.find('three_hr_pressure_tendency_mb') is not None:
            three_hr_pressure_tendency_mb = metar.find('three_hr_pressure_tendency_mb').text
        else:
            three_hr_pressure_tendency_mb = None
        if metar.find('maxT_c') is not None:
            maxT_c = metar.find('maxT_c').text
        else:
            maxT_c = None
        if metar.find('minT_c') is not None:
            minT_c = metar.find('minT_c').text
        else:
            minT_c = None
        if metar.find('maxT24hr_c') is not None:
            maxT24hr_c = metar.find('maxT24hr_c').text
        else:
            maxT24hr_c = None
        if metar.find('minT24hr_c') is not None:
            minT24hr_c = metar.find('minT24hr_c').text
        else:
            minT24hr_c = None
        if metar.find('precip_in') is not None:
            precip_in = metar.find('precip_in').text
        else:
            precip_in = None
        if metar.find('pcp3hr_in') is not None:
            pcp3hr_in = metar.find('pcp3hr_in').text
        else:
            pcp3hr_in = None
        if metar.find('pcp6hr_in') is not None:
            pcp6hr_in = metar.find('pcp6hr_in').text
        else:
            pcp6hr_in = None
        if metar.find('pcp24hr_in') is not None:
            pcp24hr_in = metar.find('pcp24hr_in').text
        else:
            pcp24hr_in = None
        if metar.find('snow_in') is not None:
            snow_in = metar.find('snow_in').text
        else:
            snow_in = None
        if metar.find('vert_vis_ft') is not None:
            vert_vis_ft = metar.find('vert_vis_ft').text
        else:
            vert_vis_ft = None
        if metar.find('metar_type') is not None:
            metar_type = metar.find('metar_type').text
        else:
            metar_type = None
        if metar.find('elevation_m') is not None:
            elevation_m = metar.find('elevation_m').text
        else:
            elevation_m = None

        if metar.find('corrected') is not None:
            corrected = True
        else:
            corrected = None
        if metar.find('auto') is not None:
            auto = True
        else:
            auto = None
        if metar.find('auto_station') is not None:
            auto_station = True
        else:
            auto_station = None
        if metar.find('maintenance_indicator_on') is not None:
            maintenance_indicator_on = True
        else:
            maintenance_indicator_on = None
        if metar.find('no_signal') is not None:
            no_signal = True
        else:
            no_signal = None
        if metar.find('lightning_sensor_off') is not None:
            lightning_sensor_off = True
        else:
            lightning_sensor_off = None
        if metar.find('freezing_rain_sensor_off') is not None:
            freezing_rain_sensor_off = True
        else:
            freezing_rain_sensor_off = None
        if metar.find('present_weather_sensor_off') is not None:
            present_weather_sensor_off = True
        else:
            present_weather_sensor_off = None

        sky_list = []
        base_list = []
        for condition in metar.iter('sky_condition'):
            sky_list.append(condition.get('sky_cover'))
            base_list.append(condition.get('cloud_base_ft_agl'))
        

        if len(sky_list) == 0:
            sky_list.append(None)
            sky_list.append(None)
            sky_list.append(None)
            sky_list.append(None)
        if len(sky_list) == 1:
            sky_list.append(None)
            sky_list.append(None)
            sky_list.append(None)
        if len(sky_list) == 2:
            sky_list.append(None)
            sky_list.append(None)
        if len(sky_list) == 3:
            sky_list.append(None)
        if len(base_list) == 0:
            base_list.append(None)
            base_list.append(None)
            base_list.append(None)
            base_list.append(None)
        if len(base_list) == 1:
            base_list.append(None)
            base_list.append(None)
            base_list.append(None)
        if len(base_list) == 2:
            base_list.append(None)
            base_list.append(None)
        if len(base_list) == 3:
            base_list.append(None)
        

        WX = Metar.query.filter_by(station_id=stationId, observation_time=observation_time).first()
        if WX is None:
            WXDB = Metar(raw_text=raw_text, observation_time=observation_time, station_id=stationId, latitude=latitude, longitude=longitude, temp_c=temp_c, dewpoint_c=dewpoint_c, wind_dir_degrees=wind_dir_degrees, wind_speed_kt=wind_speed_kt, wind_gust_kt=wind_gust_kt, visibility_statute_mi=visibility_statute_mi, altim_in_hg=altim_in_hg, sea_level_pressure_mb=sea_level_pressure_mb, corrected=corrected, auto=auto, auto_station=auto_station, maintenance_indicator_on=maintenance_indicator_on, no_signal=no_signal, lightning_sensor_off=lightning_sensor_off, freezing_rain_sensor_off=freezing_rain_sensor_off, present_weather_sensor_off=present_weather_sensor_off, flight_category=flightCategory, three_hr_pressure_tendency_mb=three_hr_pressure_tendency_mb, maxT_c=maxT_c, minT_c=minT_c, maxT24hr_c=maxT24hr_c, minT24hr_c=minT24hr_c, precip_in=precip_in, pcp3hr_in=pcp3hr_in, pcp6hr_in=pcp6hr_in, pcp24hr_in=pcp24hr_in, snow_in=snow_in, vert_vis_ft=vert_vis_ft, metar_type=metar_type, elevation_m=elevation_m, sky_cover1=sky_list[0], cloud_base_ft_agl1=base_list[0], sky_cover2=sky_list[1], cloud_base_ft_agl2=base_list[1], sky_cover3=sky_list[2], cloud_base_ft_ag3=base_list[2], sky_cover4=sky_list[3], cloud_base_ft_ag4=base_list[3], wx_string=wx_string)
            db.session.add(WXDB)
            db.session.commit()
            print(stationId, wx_string)
            



@app.cli.command()
def loadTAF(): 
    """Load TAF."""
    url = "https://www.aviationweather.gov/adds/dataserver_current/current/tafs.cache.xml"

    content = urllib.request.urlopen(url).read()

    root = ET.fromstring(content)
    for taf in root.iter('TAF'):
        raw_text = taf.find('raw_text').text
        station_id = taf.find('station_id').text
        issue_time = taf.find('issue_time').text
        bulletin_time = taf.find('bulletin_time').text
        valid_time_from = taf.find('valid_time_from').text
        valid_time_to = taf.find('valid_time_to').text
        if taf.find('remarks') is not None:
            remarks = taf.find('remarks').text
        else:
            remarks = None
        latitude = taf.find('latitude').text
        longitude = taf.find('longitude').text
        elevation_m = taf.find('elevation_m').text
        for forecast in taf.iter('forecast'):
            fcst_time_from = forecast.find('fcst_time_from').text
            fcst_time_to = forecast.find('fcst_time_to').text
            if forecast.find('wind_dir_degrees') is not None:
                wind_dir_degrees = forecast.find('wind_dir_degrees').text
            else:
                wind_dir_degrees = None
            if forecast.find('change_indicator') is not None:
                change_indicator = forecast.find('change_indicator').text
            else:
                change_indicator = None
            if forecast.find('time_becoming') is not None:
                time_becoming = forecast.find('time_becoming').text
            else:
                time_becoming = None
            if forecast.find('probability') is not None:
                probability = forecast.find('probability').text
            else:
                probability = None
            if forecast.find('wind_speed_kt') is not None:
                wind_speed_kt = forecast.find('wind_speed_kt').text
            else:
                wind_speed_kt = None
            if forecast.find('wind_gust_kt') is not None:
                wind_gust_kt = forecast.find('wind_gust_kt').text
            else:
                wind_gust_kt = None
            if forecast.find('wind_shear_hgt_ft_agl') is not None:
                wind_shear_hgt_ft_agl = forecast.find('wind_shear_hgt_ft_agl').text
            else:
                wind_shear_hgt_ft_agl = None
            if forecast.find('wind_shear_dir_degrees') is not None:
                wind_shear_dir_degrees = forecast.find('wind_shear_dir_degrees').text
            else:
                wind_shear_dir_degrees = None
            if forecast.find('wind_shear_speed_kt') is not None:
                wind_shear_speed_kt = forecast.find('wind_shear_speed_kt').text
            else:
                wind_shear_speed_kt = None
            if forecast.find('visibility_statute_mi') is not None:
                visibility_statute_mi = forecast.find('visibility_statute_mi').text
            else:
                visibility_statute_mi = None
            if forecast.find('altim_in_hg') is not None:
                altim_in_hg = forecast.find('altim_in_hg').text
            else:
                altim_in_hg = None
            if forecast.find('vert_vis_ft') is not None:
                vert_vis_ft = forecast.find('vert_vis_ft').text
            else:
                vert_vis_ft = None
            if forecast.find('wx_string') is not None:
                wx_string = forecast.find('wx_string').text
            else:
                wx_string = None
            if forecast.find('not_decoded') is not None:
                not_decoded = forecast.find('not_decoded').text
            else:
                not_decoded = None
            
            
            sky_cover = []
            cloud_base_ft_agl = []
            cloud_type = []
            for condition in forecast.iter('sky_condition'):
                sky_cover.append(condition.get('sky_cover'))
                cloud_base_ft_agl.append(condition.get('cloud_base_ft_agl'))
                cloud_type.append(condition.get('cloud_type'))

            if len(sky_cover) == 0:
                sky_cover.append(None)
                sky_cover.append(None)
            if len(sky_cover) == 1:
                sky_cover.append(None)
            if len(cloud_base_ft_agl) == 0:
                cloud_base_ft_agl.append(None)
                cloud_base_ft_agl.append(None)
            if len(cloud_base_ft_agl) == 1:
                cloud_base_ft_agl.append(None)
            if len(cloud_type) == 0:
                cloud_type.append(None)
                cloud_type.append(None)
            if len(cloud_type) == 1:
                cloud_type.append(None)

            turbulence_intensity = []
            turbulence_min_alt_ft_agl = []
            turbulence_max_alt_ft_agl = []
            for condition in forecast.iter('turbulence_condition'):
                turbulence_intensity.append(condition.get('turbulence_intensity'))
                turbulence_min_alt_ft_agl.append(condition.get('turbulence_min_alt_ft_agl'))
                turbulence_max_alt_ft_agl.append(condition.get('turbulence_max_alt_ft_agl'))
            
            if len(turbulence_intensity) == 0:
                turbulence_intensity.append(None)
                turbulence_intensity.append(None)
            if len(turbulence_intensity) == 1:
                turbulence_intensity.append(None)
            if len(turbulence_min_alt_ft_agl) == 0:
                turbulence_min_alt_ft_agl.append(None)
                turbulence_min_alt_ft_agl.append(None)
            if len(turbulence_min_alt_ft_agl) == 1:
                turbulence_min_alt_ft_agl.append(None)
            if len(turbulence_max_alt_ft_agl) == 0:
                turbulence_max_alt_ft_agl.append(None)
                turbulence_max_alt_ft_agl.append(None)
            if len(turbulence_max_alt_ft_agl) == 1:
                turbulence_max_alt_ft_agl.append(None)
            
            icing_intensity = []
            icing_min_alt_ft_agl = []
            icing_max_alt_ft_agl = []
            for condition in forecast.iter('icing_condition'):
                icing_intensity.append(condition.get('icing_intensity'))
                icing_min_alt_ft_agl.append(condition.get('icing_min_alt_ft_agl'))
                icing_max_alt_ft_agl.append(condition.get('icing_max_alt_ft_agl'))

            if len(icing_intensity) == 0:
                icing_intensity.append(None)
                icing_intensity.append(None)
            if len(icing_intensity) == 1:
                icing_intensity.append(None)
            if len(icing_min_alt_ft_agl) == 0:
                icing_min_alt_ft_agl.append(None)
                icing_min_alt_ft_agl.append(None)
            if len(icing_min_alt_ft_agl) == 1:
                icing_min_alt_ft_agl.append(None)
            if len(icing_max_alt_ft_agl) == 0:
                icing_max_alt_ft_agl.append(None)
                icing_max_alt_ft_agl.append(None)
            if len(icing_max_alt_ft_agl) == 1:
                icing_max_alt_ft_agl.append(None)

            if forecast.find('valid_time') is not None:
                valid_time = forecast.find('valid_time').text
            else:
                valid_time = None
            if forecast.find('sfc_temp_c') is not None:
                sfc_temp_c = forecast.find('sfc_temp_c').text
            else:
                sfc_temp_c = None
            if forecast.find('max_temp_c') is not None:
                max_temp_c = forecast.find('max_temp_c').text
            else:
                max_temp_c = None
            if forecast.find('min_temp_c') is not None:
                min_temp_c = forecast.find('min_temp_c').text
            else:
                min_temp_c = None
            

            WX = Taf.query.filter_by(station_id=station_id, issue_time=issue_time, fcst_time_from=fcst_time_from, fcst_time_to=fcst_time_to).first()
            if WX is None:
                WXDB = Taf(station_id=station_id, issue_time=issue_time, bulletin_time=bulletin_time, latitude=latitude, longitude=longitude, valid_time_from=valid_time_from, valid_time_to=valid_time_to, remarks=remarks, elevation_m=elevation_m, fcst_time_from=fcst_time_from, fcst_time_to=fcst_time_to, change_indicator=change_indicator, time_becoming=time_becoming, probability=probability, wind_dir_degrees=wind_dir_degrees, wind_speed_kt=wind_speed_kt, wind_gust_kt=wind_gust_kt, wind_shear_dir_degrees=wind_shear_dir_degrees, wind_shear_speed_kt=wind_shear_speed_kt, wind_shear_hgt_ft_agl=wind_shear_hgt_ft_agl, visibility_statute_mi=visibility_statute_mi, altim_in_hg=altim_in_hg, vert_vis_ft=vert_vis_ft, wx_string=wx_string, not_decoded=not_decoded, valid_time=valid_time, sfc_temp_c=sfc_temp_c, max_temp_c=max_temp_c, min_temp_c=min_temp_c, raw_text=raw_text, cloud_base_ft_agl1=cloud_base_ft_agl[0], cloud_base_ft_agl2=cloud_base_ft_agl[1], cloud_type1=cloud_type[0], cloud_type2=cloud_type[1], icing_intensity1=icing_intensity[0], icing_intensity2=icing_intensity[1], icing_max_alt_ft_agl1=icing_max_alt_ft_agl[0], icing_max_alt_ft_agl2=icing_max_alt_ft_agl[1], icing_min_alt_ft_agl1=icing_min_alt_ft_agl[0], icing_min_alt_ft_agl2=icing_min_alt_ft_agl[1], sky_cover1=sky_cover[0], sky_cover2=sky_cover[1], turbulence_intensity1=turbulence_intensity[0], turbulence_intensity2=turbulence_intensity[1], turbulence_max_alt_ft_agl1=turbulence_max_alt_ft_agl[0], turbulence_max_alt_ft_agl2=turbulence_max_alt_ft_agl[1], turbulence_min_alt_ft_agl1=turbulence_min_alt_ft_agl[0], turbulence_min_alt_ft_agl2=turbulence_min_alt_ft_agl[1])
                db.session.add(WXDB)
                db.session.commit()
                print(station_id, icing_intensity, icing_min_alt_ft_agl, icing_max_alt_ft_agl, turbulence_intensity, turbulence_min_alt_ft_agl, turbulence_max_alt_ft_agl, sky_cover, cloud_base_ft_agl, cloud_type)

@app.cli.command()
def loadPIREP(): 
    """Load PIREP."""
    url = "https://www.aviationweather.gov/adds/dataserver_current/current/aircraftreports.cache.xml"

    content = urllib.request.urlopen(url).read()

    root = ET.fromstring(content)
    for pirep in root.iter('AircraftReport'):
        receipt_time = pirep.find('receipt_time').text
        observation_time = pirep.find('observation_time').text
        if pirep.find('./quality_control_flags/mid_point_assumed') is not None:
            mid_point_assumed = True
        else:
            mid_point_assumed =None
        if pirep.find('./quality_control_flags/no_time_stamp') is not None:
            no_time_stamp = True
        else:
            no_time_stamp =None
        if pirep.find('./quality_control_flags/flt_lvl_range') is not None:
            flt_lvl_range = True
        else:
            flt_lvl_range =None
        if pirep.find('./quality_control_flags/above_ground_level_indicated') is not None:
            above_ground_level_indicated = True
        else:
            above_ground_level_indicated =None
        if pirep.find('./quality_control_flags/no_flt_lvl') is not None:
            no_flt_lvl = True
        else:
            no_flt_lvl =None
        if pirep.find('./quality_control_flags/bad_location') is not None:
            bad_location = True
        else:
            bad_location =None
        aircraft_ref = pirep.find('aircraft_ref').text
        latitude = pirep.find('latitude').text
        longitude = pirep.find('longitude').text
        if pirep.find('altitude_ft_msl') is not None:
            altitude_ft_msl = pirep.find('altitude_ft_msl').text
        else:
            None
        if pirep.find('visibility_statute_mi') is not None:
            visibility_statute_mi = pirep.find('visibility_statute_mi').text
        else:
            visibility_statute_mi = None
        if pirep.find('wx_string') is not None:
            wx_string = pirep.find('wx_string').text
        else:
            wx_string = None
        if pirep.find('temp_c') is not None:
            temp_c = pirep.find('temp_c').text
        else:
            temp_c = None
        if pirep.find('wind_dir_degrees') is not None:
            wind_dir_degrees = pirep.find('wind_dir_degrees').text
        else:
            wind_dir_degrees = None
        if pirep.find('wind_speed_kt') is not None:
            wind_speed_kt = pirep.find('wind_speed_kt').text
        else:
            wind_speed_kt = None
        if pirep.find('vert_gust_kt') is not None:
            vert_gust_kt = pirep.find('vert_gust_kt').text
        else:
            vert_gust_kt = None
        if pirep.find('pirep_type') is not None:
            pirep_type = pirep.find('pirep_type').text
        else:
            pirep_type = None
        raw_text = pirep.find('raw_text').text
        

        sky_cover = []
        cloud_base_ft_msl = []
        cloud_top_ft_msl = []
        for condition in pirep.iter('sky_condition'):
            sky_cover.append(condition.get('sky_cover'))
            cloud_base_ft_msl.append(condition.get('cloud_base_ft_msl'))
            cloud_top_ft_msl.append(condition.get('cloud_top_ft_msl'))

        if len(sky_cover) == 0:
            sky_cover.append(None)
            sky_cover.append(None)
        if len(sky_cover) == 1:
            sky_cover.append(None)
        if len(cloud_base_ft_msl) == 0:
            cloud_base_ft_msl.append(None)
            cloud_base_ft_msl.append(None)
        if len(cloud_base_ft_msl) == 1:
            cloud_base_ft_msl.append(None)
        if len(cloud_top_ft_msl) == 0:
            cloud_top_ft_msl.append(None)
            cloud_top_ft_msl.append(None)
        if len(cloud_top_ft_msl) == 1:
            cloud_top_ft_msl.append(None)

        turbulence_type = []
        turbulence_intensity = []
        turbulence_base_ft_msl = []
        turbulence_top_ft_msl = []
        turbulence_freq = []
        for condition in pirep.iter('turbulence_condition'):
            turbulence_type.append(condition.get('turbulence_type'))
            turbulence_intensity.append(condition.get('turbulence_intensity'))
            turbulence_base_ft_msl.append(condition.get('turbulence_base_ft_msl'))
            turbulence_top_ft_msl.append(condition.get('turbulence_top_ft_msl'))
            turbulence_freq.append(condition.get('turbulence_freq'))

        
        if len(turbulence_type) == 0:
            turbulence_type.append(None)
            turbulence_type.append(None)
        if len(turbulence_type) == 1:
            turbulence_type.append(None)
        if len(turbulence_intensity) == 0:
            turbulence_intensity.append(None)
            turbulence_intensity.append(None)
        if len(turbulence_intensity) == 1:
            turbulence_intensity.append(None)
        if len(turbulence_base_ft_msl) == 0:
            turbulence_base_ft_msl.append(None)
            turbulence_base_ft_msl.append(None)
        if len(turbulence_base_ft_msl) == 1:
            turbulence_base_ft_msl.append(None)
        if len(turbulence_top_ft_msl) == 0:
            turbulence_top_ft_msl.append(None)
            turbulence_top_ft_msl.append(None)
        if len(turbulence_top_ft_msl) == 1:
            turbulence_top_ft_msl.append(None)
        if len(turbulence_freq) == 0:
            turbulence_freq.append(None)
            turbulence_freq.append(None)
        if len(turbulence_freq) == 1:
            turbulence_freq.append(None)
        
        icing_type = []
        icing_intensity = []
        icing_base_ft_msl = []
        icing_top_ft_msl = []
        for condition in pirep.iter('icing_condition'):
            icing_type.append(condition.get('icing_type'))
            icing_intensity.append(condition.get('icing_intensity'))
            icing_base_ft_msl.append(condition.get('icing_base_ft_msl'))
            icing_top_ft_msl.append(condition.get('icing_top_ft_msl'))

        if len(icing_type) == 0:
            icing_type.append(None)
            icing_type.append(None)
        if len(icing_type) == 1:
            icing_type.append(None)
        if len(icing_intensity) == 0:
            icing_intensity.append(None)
            icing_intensity.append(None)
        if len(icing_intensity) == 1:
            icing_intensity.append(None)
        if len(icing_base_ft_msl) == 0:
            icing_base_ft_msl.append(None)
            icing_base_ft_msl.append(None)
        if len(icing_base_ft_msl) == 1:
            icing_base_ft_msl.append(None)
        if len(icing_top_ft_msl) == 0:
            icing_top_ft_msl.append(None)
            icing_top_ft_msl.append(None)
        if len(icing_top_ft_msl) == 1:
            icing_top_ft_msl.append(None)

        PIREP = Pirep.query.filter_by(receipt_time=receipt_time, observation_time=observation_time, aircraft_ref=aircraft_ref).first()
        if PIREP is None:
            WXPP = Pirep(receipt_time=receipt_time ,observation_time=observation_time, mid_point_assumed=mid_point_assumed, no_time_stamp=no_time_stamp, flt_lvl_range=flt_lvl_range, above_ground_level_indicated=above_ground_level_indicated, no_flt_lvl=no_flt_lvl, bad_location=bad_location, aircraft_ref=aircraft_ref, latitude=latitude, longitude=longitude, altitude_ft_msl=altitude_ft_msl, sky_cover1=sky_cover[0], sky_cover2=sky_cover[1], cloud_base_ft_msl1=cloud_base_ft_msl[0], cloud_base_ft_msl2=cloud_base_ft_msl[1], cloud_top_ft_msl1=cloud_top_ft_msl[0], cloud_top_ft_msl2=cloud_top_ft_msl[1], turbulence_type1=turbulence_type[0], turbulence_type2=turbulence_type[1], turbulence_intensity1=turbulence_intensity[0], turbulence_intensity2=turbulence_intensity[1], turbulence_base_ft_msl1=turbulence_base_ft_msl[0], turbulence_base_ft_msl2=turbulence_base_ft_msl[1], turbulence_top_ft_msl1=turbulence_top_ft_msl[0], turbulence_top_ft_msl2=turbulence_top_ft_msl[1], turbulence_freq1=turbulence_freq[0], turbulence_freq2=turbulence_freq[1], icing_type1=icing_type[0], icing_type2=icing_type[1], icing_intensity1=icing_intensity[0], icing_intensity2=icing_intensity[1], icing_base_ft_msl1=icing_base_ft_msl[0], icing_base_ft_msl2=icing_base_ft_msl[1], icing_top_ft_msl1=icing_top_ft_msl[0], icing_top_ft_msl2=icing_top_ft_msl[1], visibility_statute_mi=visibility_statute_mi, wx_string=wx_string, temp_c=temp_c, wind_dir_degrees=wind_dir_degrees, wind_speed_kt=wind_speed_kt, vert_gust_kt=vert_gust_kt, pirep_type=pirep_type, raw_text=raw_text)
            db.session.add(WXPP)
            db.session.commit()