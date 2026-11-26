import os

import parseShips
import renderUpload

def clearRenders():
    print('clearing previous renders')
    for root, dirs, files in os.walk('Resources\MapImages'):
        for file in files:
            os.remove(os.path.join(root, file))
            os.rmdir(root)

if __name__ == '__main__':
    clearRenders()
    shipRenders = parseShips.run(full=True)
    renderUpload.uploadImages(renderCache=shipRenders, rate=2, prefix='Ship')
