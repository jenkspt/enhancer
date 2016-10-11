from googleapiclient.discovery import build
from pandas import read_csv
from googleapiclient.http import BatchHttpRequest
from urllib.parse import urlparse

class GoogleFaces():
    def __init__(self, names_tsv):
        df = read_csv(names_tsv, sep='\t', index_col='Rank')
        male, female = list(df['Name']), list(df['Name.1'])
        self.names = male + female

        self.service = build("customsearch", "v1", developerKey="AIzaSyCoe_KHDrXCdnq5SEnpbCuaYUratYAccQQ")


    def callback(self, request_id, response, exception):
        if exception:
            # Do something with the exception
            print('Exception: ', exception)
            print('Last Start = ', request_id)
        else:
            # Do something with the response
            for item in response['items']:
                parsed = urlparse(item['link'])
                clean = '{}://{}{}'.format(parsed.scheme, parsed.netloc, parsed.path)
                self.links.append(clean)

    def get_faces(self, name, pages=1, start=1):
        batch = self.service.new_batch_http_request(callback=self.callback)
        self.links = []
        for _ in range(pages):

            batch.add(self.service.cse().list(
                q='Robert',
                cx='002573093675242581899:61hr8dhak8c',
                exactTerms='400x400',
                filter='1',
                searchType='image',
                imgColorType='color',
                imgType='face',
                safe='high',
                fields='items/link',
                start=start,
                num='10'
            ), request_id=str(start))

            start += 10

        batch.execute()
        with open('../../data/google/{}.txt'.format(name), 'w') as f:
            f.write('\n'.join(self.links))

if __name__ == '__main__':
    robert = GoogleFaces('../../data/google/common_names.tsv')
    robert.get_faces('George', 100)