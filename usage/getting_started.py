from exhentai import ExhentaiOption

# start with creating an option object through a specific file
option = ExhentaiOption.from_file('../option/all_in_one.yml')
# equivalent to below: by multiple files (client.yml, cookies.yml, download.yml) in a dir
option = ExhentaiOption.from_dir('../option/')

# call download_gallery method
option.download_gallery_by_url('https://exhentai.org/g/2768121/e281882c85/')
