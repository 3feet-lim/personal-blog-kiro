# 요구사항 문서

## 소개

테크 블로그와 가족 데일리 사진을 하나의 플랫폼에서 관리하는 통합 블로그 시스템입니다. 마크다운 기반 글 작성, 이미지 업로드, 계층적 카테고리 구조, 그리고 콘텐츠별 접근 권한 관리를 제공합니다.

## 용어집

- **Blog_System**: 통합 블로그 플랫폼의 전체 시스템

- **Post_Service**: 블로그 포스트 생성, 수정, 삭제, 조회를 담당하는 서비스

- **Category_Service**: 폴더/카테고리 구조 관리를 담당하는 서비스

- **Auth_Service**: JWT 기반 사용자 인증 및 권한 관리를 담당하는 서비스

- **Image_Service**: 이미지 업로드, 리사이징, 저장을 담당하는 서비스

- **User**: 시스템에 등록된 사용자 (관리자 또는 가족 구성원)

- **Admin**: 글 작성 및 시스템 관리 권한을 가진 사용자

- **Family_Member**: 가족 사진 열람 권한을 가진 인증된 사용자

- **Post**: 마크다운 기반 블로그 글

- **Category**: 포스트를 분류하는 계층적 폴더 구조

- **Visibility**: 포스트의 공개 범위 (PUBLIC 또는 PRIVATE)

- **Tag_Service**: 태그 생성, 수정, 삭제 및 포스트-태그 관계 관리를 담당하는 서비스

- **Tag**: 포스트에 할당할 수 있는 횡단적 분류 키워드 (예: "Python", "Docker", "React")

- **Frontend_App**: Next.js 기반 프론트엔드 애플리케이션

- **Error_Boundary**: 예기치 않은 에러 발생 시 사용자 친화적 에러 페이지를 표시하는 React 컴포넌트

- **Skeleton_UI**: 콘텐츠 로딩 중 레이아웃 형태의 플레이스홀더를 표시하는 UI 컴포넌트

## 요구사항

### 요구사항 1: 사용자 인증

**사용자 스토리:** 관리자로서, 시스템에 로그인하여 글을 작성하고 관리할 수 있기를 원합니다.

#### 인수 조건

1. WHEN 사용자가 유효한 이메일과 비밀번호로 로그인 요청을 보내면 THEN Auth_Service SHALL 액세스 토큰과 리프레시 토큰을 반환한다

2. WHEN 사용자가 잘못된 자격 증명으로 로그인 요청을 보내면 THEN Auth_Service SHALL 인증 실패 오류를 반환한다

3. WHEN 유효한 액세스 토큰이 포함된 요청이 들어오면 THEN Auth_Service SHALL 해당 사용자 정보를 추출하여 요청을 처리한다

4. WHEN 만료된 액세스 토큰이 포함된 요청이 들어오면 THEN Auth_Service SHALL 토큰 만료 오류를 반환한다

5. WHEN 유효한 리프레시 토큰으로 토큰 갱신 요청이 들어오면 THEN Auth_Service SHALL 새로운 액세스 토큰을 발급한다

6. THE Auth_Service SHALL 비밀번호를 bcrypt 해시로 저장한다

7. THE Auth_Service SHALL JWT 토큰에 사용자 ID와 역할 정보를 포함한다

### 요구사항 2: 포스트 작성 및 관리

**사용자 스토리:** 관리자로서, 마크다운 형식으로 테크 블로그 글과 가족 사진 글을 작성하고 관리할 수 있기를 원합니다.

#### 인수 조건

1. WHEN 관리자가 제목, 내용, 카테고리, 공개 범위를 포함한 포스트 생성 요청을 보내면 THEN Post_Service SHALL 새 포스트를 생성하고 저장한다

2. WHEN 관리자가 기존 포스트의 수정 요청을 보내면 THEN Post_Service SHALL 해당 포스트의 내용을 업데이트한다

3. WHEN 관리자가 포스트 삭제 요청을 보내면 THEN Post_Service SHALL 해당 포스트를 삭제한다

4. THE Post_Service SHALL 포스트 내용을 마크다운 형식으로 저장한다

5. THE Post_Service SHALL 각 포스트에 생성일시와 수정일시를 기록한다

6. WHEN 포스트가 생성되면 THEN Post_Service SHALL 고유한 슬러그(slug)를 자동 생성한다

7. IF 동일한 슬러그가 이미 존재하면 THEN Post_Service SHALL 숫자 접미사를 추가하여 고유성을 보장한다

### 요구사항 3: 카테고리 관리

**사용자 스토리:** 관리자로서, 포스트를 주제별로 분류할 수 있는 계층적 카테고리 구조를 관리할 수 있기를 원합니다.

#### 인수 조건

1. WHEN 관리자가 카테고리 생성 요청을 보내면 THEN Category_Service SHALL 새 카테고리를 생성한다

2. WHEN 관리자가 부모 카테고리를 지정하여 카테고리 생성 요청을 보내면 THEN Category_Service SHALL 해당 부모 아래에 하위 카테고리를 생성한다

3. WHEN 카테고리 목록 조회 요청이 들어오면 THEN Category_Service SHALL 계층 구조를 유지한 카테고리 트리를 반환한다

4. WHEN 관리자가 카테고리 삭제 요청을 보내면 THEN Category_Service SHALL 해당 카테고리와 하위 카테고리를 삭제한다

5. IF 삭제 대상 카테고리에 포스트가 존재하면 THEN Category_Service SHALL 삭제를 거부하고 오류를 반환한다

6. THE Category_Service SHALL 각 카테고리에 고유한 슬러그를 부여한다

### 요구사항 4: 포스트 조회 및 접근 권한

**사용자 스토리:** 방문자로서, 공개된 테크 블로그 글을 읽을 수 있고, 가족 구성원으로서 로그인 후 가족 사진을 볼 수 있기를 원합니다.

#### 인수 조건

1. WHEN 인증되지 않은 사용자가 포스트 목록을 요청하면 THEN Post_Service SHALL PUBLIC 공개 범위의 포스트만 반환한다

2. WHEN 인증된 가족 구성원이 포스트 목록을 요청하면 THEN Post_Service SHALL PUBLIC과 PRIVATE 모든 포스트를 반환한다

3. WHEN 인증되지 않은 사용자가 PRIVATE 포스트에 접근하면 THEN Post_Service SHALL 접근 거부 오류를 반환한다

4. WHEN 사용자가 카테고리별 포스트 목록을 요청하면 THEN Post_Service SHALL 해당 카테고리의 포스트만 필터링하여 반환한다

5. WHEN 사용자가 포스트 상세 조회를 요청하면 THEN Post_Service SHALL 마크다운 내용과 메타데이터를 반환한다

6. THE Post_Service SHALL 포스트 목록을 페이지네이션하여 반환한다

### 요구사항 5: 이미지 업로드 및 처리

**사용자 스토리:** 관리자로서, 포스트에 이미지를 첨부할 수 있고, 업로드된 이미지가 자동으로 최적화되기를 원합니다.

#### 인수 조건

1. WHEN 관리자가 이미지 업로드 요청을 보내면 THEN Image_Service SHALL 이미지를 MinIO 스토리지에 저장한다

2. WHEN 이미지가 업로드되면 THEN Image_Service SHALL 원본 이미지를 지정된 최대 크기로 리사이징한다

3. WHEN 이미지가 업로드되면 THEN Image_Service SHALL 썸네일 이미지를 생성한다

4. THE Image_Service SHALL 업로드된 이미지의 고유 URL을 반환한다

5. WHEN 이미지 URL 요청이 들어오면 THEN Image_Service SHALL MinIO에서 이미지를 조회하여 반환한다

6. IF 지원하지 않는 이미지 형식이 업로드되면 THEN Image_Service SHALL 형식 오류를 반환한다

7. THE Image_Service SHALL JPEG, PNG, GIF, WebP 형식을 지원한다

### 요구사항 6: 사용자 관리

**사용자 스토리:** 관리자로서, 가족 구성원 계정을 생성하고 관리할 수 있기를 원합니다.

#### 인수 조건

1. WHEN 관리자가 새 사용자 생성 요청을 보내면 THEN Auth_Service SHALL 지정된 역할로 새 사용자를 생성한다

2. THE Auth_Service SHALL 사용자 역할을 ADMIN 또는 FAMILY_MEMBER로 구분한다

3. WHEN 관리자가 사용자 목록 조회 요청을 보내면 THEN Auth_Service SHALL 모든 사용자 정보를 반환한다

4. WHEN 관리자가 사용자 삭제 요청을 보내면 THEN Auth_Service SHALL 해당 사용자를 비활성화한다

5. THE Auth_Service SHALL 이메일 주소의 고유성을 보장한다

### 요구사항 7: API 응답 형식

**사용자 스토리:** 프론트엔드 개발자로서, 일관된 API 응답 형식을 통해 효율적으로 개발할 수 있기를 원합니다.

#### 인수 조건

1. THE Blog_System SHALL 모든 성공 응답에 data 필드를 포함한다

2. THE Blog_System SHALL 모든 오류 응답에 error 필드와 message 필드를 포함한다

3. THE Blog_System SHALL 목록 응답에 페이지네이션 메타데이터를 포함한다

4. THE Blog_System SHALL JSON 형식으로 응답한다

5. IF 요청 데이터가 유효하지 않으면 THEN Blog_System SHALL 상세한 유효성 검사 오류 메시지를 반환한다


### 요구사항 8: 태그 관리

**사용자 스토리:** 관리자로서, 포스트에 태그를 할당하여 카테고리와 별도로 횡단적 분류를 할 수 있기를 원합니다.

#### 인수 조건

1. WHEN 관리자가 태그 생성 요청을 보내면 THEN Tag_Service SHALL 새 태그를 생성한다

2. WHEN 관리자가 태그 수정 요청을 보내면 THEN Tag_Service SHALL 해당 태그의 이름을 업데이트한다

3. WHEN 관리자가 태그 삭제 요청을 보내면 THEN Tag_Service SHALL 해당 태그를 삭제하고 포스트-태그 관계를 제거한다

4. WHEN 관리자가 포스트에 태그 할당 요청을 보내면 THEN Tag_Service SHALL 해당 포스트와 태그의 다대다 관계를 생성한다

5. WHEN 관리자가 포스트에서 태그 제거 요청을 보내면 THEN Tag_Service SHALL 해당 포스트-태그 관계를 삭제한다

6. WHEN 사용자가 특정 태그로 포스트 목록을 요청하면 THEN Tag_Service SHALL 해당 태그가 할당된 포스트만 필터링하여 반환한다

7. THE Tag_Service SHALL 태그 이름의 고유성을 보장한다

8. WHEN 태그가 생성되면 THEN Tag_Service SHALL 태그 이름으로부터 고유한 슬러그를 자동 생성한다

9. IF 동일한 태그 이름이 이미 존재하면 THEN Tag_Service SHALL 중복 오류를 반환한다

### 요구사항 9: 에러 및 로딩 상태 UI

**사용자 스토리:** 사용자로서, 에러 발생 시 친화적인 안내 페이지를 보고, 콘텐츠 로딩 중 시각적 피드백을 받을 수 있기를 원합니다.

#### 인수 조건

1. WHEN 사용자가 존재하지 않는 페이지에 접근하면 THEN Frontend_App SHALL not-found.tsx를 통해 404 안내 페이지를 표시한다

2. WHEN 예기치 않은 런타임 에러가 발생하면 THEN Frontend_App SHALL error.tsx의 Error_Boundary를 통해 사용자 친화적 에러 페이지를 표시한다

3. WHILE 페이지 콘텐츠가 로딩 중이면 THEN Frontend_App SHALL loading.tsx를 통해 Skeleton_UI를 표시한다

4. THE Frontend_App SHALL 404 페이지에 홈으로 돌아가기 링크를 포함한다

5. THE Frontend_App SHALL 에러 페이지에 다시 시도하기 버튼을 포함한다

6. WHEN 에러 페이지의 다시 시도하기 버튼이 클릭되면 THEN Frontend_App SHALL 현재 경로를 다시 로드한다

7. THE Frontend_App SHALL 포스트 목록 페이지와 포스트 상세 페이지에 각각 적합한 Skeleton_UI를 제공한다
