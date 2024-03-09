import pathlib

import appdirs

package_user_dir = pathlib.Path(appdirs.user_data_dir('ontolutils'))
package_user_dir.mkdir(parents=True, exist_ok=True)


def get_cache_dir() -> pathlib.Path:
    cache_dir = package_user_dir / 'cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
