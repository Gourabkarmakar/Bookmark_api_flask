from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from

bookmarks = Blueprint('bookmarks', __name__, url_prefix="/api/v1/bookmarks")

# Get or post data Endpoint
# fetch all bookmarks use this Endpoint


@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handel_bookmarks():

    current_user_id = get_jwt_identity()
    if request.method == "POST":
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'enter valid url'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "error": "url already exist"
            }), HTTP_409_CONFLICT

        bookmark_add = Bookmark(url=url, body=body, user_id=current_user_id)
        db.session.add(bookmark_add)
        db.session.commit()

        return jsonify({
            "id": bookmark_add.id,
            "url": bookmark_add.url,
            "body": bookmark_add.body,
            "short url": bookmark_add.short_url,
            "visitor": bookmark_add.visiters,
            "created by": bookmark_add.created_at,
            "update by": bookmark_add.update_at
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmark_list = Bookmark.query.filter_by(
            user_id=current_user_id).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in bookmark_list.items:
            data.append({
                "id": bookmark.id,
                "url": bookmark.url,
                "body": bookmark.body,
                "short url": bookmark.short_url,
                "visitor": bookmark.visiters,
                "created by": bookmark.created_at,
                "update by": bookmark.update_at
            })

        meta = {
            "page": bookmark_list.page,
            "pages": bookmark_list.pages,
            "total_counts": bookmark_list.total,
            "prev_page": bookmark_list.prev_num,
            "next_page": bookmark_list.next_num,
            "has_prev": bookmark_list.has_prev,
            "has_next": bookmark_list.has_next,
        }
        return jsonify({
            "data": data,
            "meta": meta,
        }), HTTP_200_OK

# Get one bookmark endpoint


@bookmarks.get('/<int:id>')
@jwt_required()
def fetch_one_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": "bookmark not found",
        }), HTTP_400_BAD_REQUEST

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "body": bookmark.body,
        "short url": bookmark.short_url,
        "visitor": bookmark.visiters,
        "created by": bookmark.created_at,
        "update by": bookmark.update_at
    }), HTTP_200_OK


# Edit Endpoint
@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": "bookmark not found"
        }), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({"error": "invalid url"}), HTTP_404_NOT_FOUND

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        "url": bookmark.url,
        "body": bookmark.body,
        "short url": bookmark.short_url,
        "visitor": bookmark.visiters,
        "created by": bookmark.created_at,
        "update by": bookmark.update_at
    }), HTTP_200_OK


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmarks(id):
    current_user = get_jwt_identity()

    d_bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not d_bookmark:
        return jsonify({
            "error": "bookmark not found"
        }), HTTP_404_NOT_FOUND

    db.session.delete(d_bookmark)
    db.session.commit()
    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get('/stats')
@jwt_required()
@swag_from('./docs/bookmark/statsbook.yaml')
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            "id": item.id,
            "visits": item.visiters,
            "url": item.url,
            "short_url": item.short_url,
        }
        data.append(new_link)

    return jsonify({
        "data": data
    }), HTTP_200_OK