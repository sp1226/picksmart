from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Product
import os

class Command(BaseCommand):
    help = '상품 이미지 업데이트'

    def handle(self, *args, **kwargs):
        # 이미지 파일 매핑
        image_mapping = {
            'IT전문서적': 'IT전문서적.jpeg',
            '고급스킨케어세트': '고급스킨케어세트.jpeg',
            '과학도서': '과학도서.jpeg',
            '게이밍노트북': '게이밍노트북.png',
            '게이밍마우스': '게이밍마우스.jpeg',
            '골프클럽세트': '골프클럽세트.jpeg',
            '기계식키보드': '기계식키보드.png',
            '기초화장품세트': '기초화장품세트.png',
            '노이즈캔슬링헤드폰': '노이즈캔슬링헤드폰.jpeg',
            '다이어리': '다이어리.jpeg',
            '러닝화': '러닝화.png',
            '만화책': '만화책.jpeg',
            '메이크업팔레트': '메이크업팔레트.png',
            '명품가방': '명품가방.jpeg',
            '명품벨트': '명품벨트.png',
            '명품선글라스': '명품선글라스.png',
            '명품지갑': '명품지갑.png',
            '명품향수': '명품향수.png',
            '미술용품세트': '미술용품세트.jpeg',
            '소설책': '소설책.png',
            '수험서': '수험서.jpeg',
            '스케치북': '스케치북.jpeg',
            '스마트워치': '스마트워치.png',
            '요가매트': '요가매트.png',
            '자기계발서': '자기계발서.jpeg',
            '테니스라켓': '테니스라켓.png',
            '태블릿PC': '태블릿PC.png',
            '프리미엄립스틱': '프리미엄립스틱.jpeg',
            '프리미엄만년필': '프리미엄만년필.jpeg',
            '프리미엄파운데이션': '프리미엄파운데이션.png',
            '필기구세트': '필기구세트.jpeg',
            '헬스용품세트': '헬스용품세트.png',
            '크로스백': '크로스백.jpeg',
            '캐주얼백팩': '캐주얼백팩.jpeg',
            '취미키트': '취미키트.jpeg',
            '등산용품': '등산용품.jpeg'
        }

        # 이미지 디렉토리 경로
        media_root = 'media'
        products_dir = os.path.join(media_root, 'products')
        
        # 디렉토리 존재 확인
        if not os.path.exists(products_dir):
            self.stdout.write(self.style.WARNING(f'Creating directory: {products_dir}'))
            os.makedirs(products_dir)
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        self.stdout.write(self.style.NOTICE('Starting image update process...'))

        # 각 상품의 이미지 업데이트
        for product in Product.objects.all():
            try:
                if product.title in image_mapping:
                    image_name = image_mapping[product.title]
                    image_path = os.path.join('products', image_name)
                    full_path = os.path.join(media_root, 'products', image_name)
                    
                    if os.path.exists(full_path):
                        # 기존 이미지가 있다면 삭제
                        if product.image:
                            product.image.delete(save=False)
                        
                        # 새 이미지 설정
                        with open(full_path, 'rb') as img_file:
                            product.image.save(image_name, File(img_file), save=True)
                        success_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Updated image for {product.title}')
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Image file not found: {full_path}')
                        )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠ No image mapping for: {product.title}')
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {product.title}: {str(e)}')
                )

        # 최종 결과 출력
        self.stdout.write('\nUpdate process completed:')
        self.stdout.write(self.style.SUCCESS(f'Successfully updated: {success_count}'))
        self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))