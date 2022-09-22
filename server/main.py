from ast import Bytes
from dataclasses import dataclass
from tempfile import NamedTemporaryFile

# from analyzer import ChartAnalyzer
from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles


@dataclass
class PreviewResponse():
    preview: Bytes | None


# analyzer = ChartAnalyzer()
app = FastAPI(
    title='SweetPotato Chart Preview Server',
    description='SUS chart preview generator',
    version='0.1.0'
)


@app.get('/health_check')
async def health_check():
    """生存確認用エンドポイント"""
    return {'message': 'Server is working'}


@app.post('/preview', response_model=PreviewResponse)
async def generate_preview(file: UploadFile):
    """SUSファイルからプレビューを生成するエンドポイント"""
    if not file.filename.endswith('.sus') or\
            not file.content_type == 'application/octet-stream':
        return {'message': 'Invalid file format'}
    with NamedTemporaryFile('wb', delete=False) as f:
        content = await file.read()
        f.write(content)
        f.seek(0)
        # data = analyzer.get_feature_values_from_sus(f.name)
        # result = predictor.predict([data])
    return PreviewResponse(preview=None)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, debug=True)
