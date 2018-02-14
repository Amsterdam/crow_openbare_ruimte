
DROP TABLE IF EXISTS inspections_total; 
SELECT  --a."allResultsAboveMinimumValue", 
	a."createdAt" as inspection_created_at, 
	a."creatingUserId" as creating_user_id, 
        a.id as inspection_round_id, 
        a."inspectionRoundName" as inspection_round_name, 
        a."location.geoJsonProperties.x" as x,
        a."location.geoJsonProperties.y" as y, 
        a."location.locationId" as location_id, 
        a."modifiedAt" as inspection_round_modified_at, 
        a."photos.0.id" as photo_id, 
        a."photos.0.uri" as photo_uri, 
        a."roundResultCompletedAt" as inspection_round_completed_at, 
        a.score as score_id, 
        b.description as score_description, 
        b.inspection_type_id, 
        b.inspection_type_name, 
        b.measuring_desc as score_measuring_description, 
        b.name as score,
        ST_X(ST_CENTROID(ST_GeomFromGeoJSON(geojson))) as lat,
        ST_Y(ST_CENTROID(ST_GeomFromGeoJSON(geojson))) as lon,
        a.geojson, 
        ST_SetSRID(ST_GeomFromGeoJSON(geojson), 4326) as geom
INTO inspections_total
FROM (SELECT * FROM public.inspections_area
      UNION ALL SELECT * FROM public.inspections_object) as a
INNER JOIN 
    (SELECT * FROM public.inspectietypes) as b
  ON
    a."inspectionItem.id"::text||a.score::text = b.inspection_type_id::text || b.id::text;

CREATE index ON inspections_total USING GIST(geom);

DROP TABLE if exists inspections_total_areas CASCADE;
SELECT 
        e.inspection_created_at, 
	e.creating_user_id, 
        e.inspection_round_id, 
        e.inspection_round_name, 
        e.x,
        e.y, 
        e.location_id, 
        e.inspection_round_modified_at, 
        e.photo_id, 
        e.photo_uri, 
        e.inspection_round_completed_at, 
        e.score as score_id, 
        e.score_description, 
        e.inspection_type_id, 
        e.inspection_type_name, 
        e.score_measuring_description, 
        e.score,
        e.lat,
        e.lon,
        e.geojson, 
        e.stadsdeelcode,
        e.stadsdeelnaam,
        g.naam as gebiedsnaam, 
        g.code as gebiedscode,
        e.wijkcode,
        e.wijknaam,
        e.buurtnaam,
        e.buurtcode
INTO inspections_total_areas
FROM
   (SELECT 
     c.*,
     d.stadsdeelcode,
     d.stadsdeelnaam,
     d.wijkcode,
     d.wijknaam,
     d.buurtnaam,
     d.buurtcode
  FROM 
    (select * from inspections_total) as c, 
    (SELECT
       s.naam as stadsdeelnaam,
       s.code as stadsdeelcode,
       a.wijknaam,
       a.wijkcode,
       a.buurtnaam,
       s.code || a.code as buurtcode,
       a.wkb_geometry
FROM
   (SELECT 
       w.vollcode as wijkcode,
       b.naam as buurtnaam,
       w.naam as wijknaam,
       b.code as code,
       b.wkb_geometry
    FROM  buurt as b 
    LEFT JOIN buurtcombinatie as w
    ON RIGHT(w.vollcode,2) = LEFT(b.code,2)) as a
LEFT JOIN stadsdeel as s 
ON s.code = LEFT(a.wijkcode,1)) as d
  WHERE ST_WITHIN(ST_TRANSFORM(ST_CENTROID(c.geom), 28992), d.wkb_geometry)
  ) as e,
  gebiedsgerichtwerken as g
WHERE ST_WITHIN(ST_TRANSFORM(ST_CENTROID(e.geom), 28992), g.wkb_geometry);
--ALTER TABLE crowscores_totaal 
--ADD PRIMARY KEY (id);

