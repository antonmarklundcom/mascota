"""Build deterministic, explicit allowlisted Hostinger private-sibling releases."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from release_metadata import encoded, metadata, release_files

def build(root, output):
    files = release_files(root)
    release = metadata(root, files)
    files['public_html/release.json'] = encoded(release)
    output.mkdir(parents=True, exist_ok=True)
    package = output/('mascota-hostinger-'+release['version']+'.zip')
    with tempfile.NamedTemporaryFile(dir=output, suffix='.tmp', delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name,body in sorted(files.items()):
                entry = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry,body)
        manifest = {**release, 'package':package.name, 'sha256':hashlib.sha256(temporary.read_bytes()).hexdigest(),
                    'files':{name:hashlib.sha256(body).hexdigest() for name,body in sorted(files.items())},
                    'containsSecrets':False, 'containsCustomerData':False}
        manifest_path = package.with_suffix('.manifest.json')
        # Both outputs are immutable; reject conflicts before writing either output.
        for path,body in [(package,temporary.read_bytes()),(manifest_path,encoded(manifest))]:
            if path.exists() and path.read_bytes()!=body: raise ValueError('Refusing to overwrite differing release: '+str(path))
        if not package.exists(): os.replace(temporary,package)
        if not manifest_path.exists(): manifest_path.write_bytes(encoded(manifest))
        return manifest
    finally:
        temporary.unlink(missing_ok=True)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    print(json.dumps(build(args.root.resolve(),args.output.resolve()),indent=2))
