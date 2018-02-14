SELECT DISTINCT
       a.stadsdeelcode,
       a.buurtcode,
       w.vollcode as wijkcode,
       a.stadsdeelnaam,
       a.buurtnaam,
       w.naam as wijknaam,
       a.wkb_geometry
     FROM
     (  SELECT 
        s.naam as stadsdeelnaam,
        s.code as stadsdeelcode,
        b.naam as buurtnaam,
        s.code || b.code as buurtcode,
        b.wkb_geometry
        FROM 
          buurt as b, 
          stadsdeel as s
        WHERE ST_WITHIN(ST_CENTROID(b.wkb_geometry),s.wkb_geometry)
      ) as a, 
      buurtcombinatie as w


 SELECT 
       s.code as stadsdeelcode,
       s.code || b.code as buurtcode,
       w.vollcode as wijkcode,
       s.naam as stadsdeelnaam,
       b.naam as buurtnaam,
       w.naam as wijknaam,
       b.wkb_geometry
 FROM  buurt as b, 
       buurtcombinatie as w, 
       stadsdeel as s 
 WHERE s.code = LEFT(b.code,1) AND w.code = LEFT(b.code,2)