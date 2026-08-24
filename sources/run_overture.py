"""Overture Maps buildings -> California GeoPackage. Replaces the 2021 Microsoft layer.
Carries roof_shape / roof_material / facade_material / height, which Microsoft did not."""
import duckdb, os, time
REL = "2026-08-19.0"
P = f"s3://overturemaps-us-west-2/release/{REL}/theme=buildings/type=building/*.parquet"
OUT = "data/index/overture_buildings_ca.gpkg"
CA = dict(xmin=-124.50, xmax=-114.10, ymin=32.50, ymax=42.05)

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = duckdb.connect()
c.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
c.execute("SET preserve_insertion_order=false; SET memory_limit='6GB';")
t0 = time.time()
c.execute(f"""
COPY (
  SELECT id, geometry AS geom, height, num_floors, level, subtype, class,
         roof_shape, roof_material, roof_color, facade_material,
         sources[1].dataset AS src_dataset, sources[1].update_time AS src_updated
  FROM read_parquet('{P}')
  WHERE bbox.xmin > {CA['xmin']} AND bbox.xmax < {CA['xmax']}
    AND bbox.ymin > {CA['ymin']} AND bbox.ymax < {CA['ymax']}
) TO '{OUT}' WITH (FORMAT GDAL, DRIVER 'GPKG');
""")
n = c.execute(f"SELECT count(*) FROM st_read('{OUT}')").fetchone()[0]
print(f"OVERTURE DONE release={REL} rows={n:,} "
      f"size={os.path.getsize(OUT)/1e9:.2f}GB in {time.time()-t0:.0f}s", flush=True)
