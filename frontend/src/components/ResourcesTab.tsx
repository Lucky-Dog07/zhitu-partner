import React, { useState } from 'react';
import { Tabs, Card, Row, Col, Empty, Tag, Rate, Button, Space } from 'antd';
import { BookOutlined, TrophyOutlined, ReadOutlined, LinkOutlined, PlusOutlined } from '@ant-design/icons';
import type { Course, Book, Certification } from '../types';
import GenerateContentButton from './GenerateContentButton';

interface ResourcesTabProps {
  pathId: number;
  courses?: Course[];
  books?: Book[];
  certifications?: Certification[];
  onCoursesGenerated: (content: any) => void;
  onBooksGenerated: (content: any) => void;
  onCertificationsGenerated: (content: any) => void;
}

const ResourcesTab: React.FC<ResourcesTabProps> = ({
  pathId,
  courses,
  books,
  certifications,
  onCoursesGenerated,
  onBooksGenerated,
  onCertificationsGenerated
}) => {
  const [activeKey, setActiveKey] = useState('courses');

  // 课程卡片
  const CourseCard: React.FC<{ course: Course }> = ({ course }) => {
    // 平台颜色映射
    const getPlatformColor = (platform?: string) => {
      const colorMap: Record<string, string> = {
        'bilibili': '#00a1d6',
        'imooc': '#f01414',
        'geekbang': '#06c',
      };
      return colorMap[platform || ''] || '#1677ff';
    };

    return (
      <Card 
        hoverable 
        style={{ height: '100%' }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: 8 }}>
              {course.platform && (
                <Tag color={getPlatformColor(course.platform)} style={{ marginBottom: 8 }}>
                  {course.platform === 'bilibili' ? 'B站' : 
                   course.platform === 'imooc' ? '慕课网' : 
                   course.platform === 'geekbang' ? '极客时间' : course.platform}
                </Tag>
              )}
              {course.level && (
                <Tag color={
                  course.level === 'beginner' ? 'green' :
                  course.level === 'intermediate' ? 'blue' : 'red'
                }>
                  {course.level === 'beginner' ? '初级' :
                   course.level === 'intermediate' ? '中级' : '高级'}
                </Tag>
              )}
            </div>
            <h3 style={{ marginBottom: 8, fontSize: 16 }}>{course.title}</h3>
            <p style={{ color: '#666', fontSize: 14, marginBottom: 8 }}>
              {course.provider || course.author}
            </p>
            {(course.views || course.rating) && (
              <div style={{ marginBottom: 8, fontSize: 13, color: '#999' }}>
                {course.views && <span>播放：{course.views}</span>}
                {course.rating && course.rating !== 'null' && (
                  <>
                    {course.views && <span style={{ margin: '0 8px' }}>|</span>}
                    <Rate disabled defaultValue={Number(course.rating) || 0} style={{ fontSize: 12 }} />
                    <span style={{ marginLeft: 4 }}>{course.rating}</span>
                  </>
                )}
              </div>
            )}
            <p style={{ marginTop: 8, fontSize: 13, color: '#666', lineHeight: 1.6, maxHeight: 60, overflow: 'hidden' }}>
              {course.description}
            </p>
          </div>
          <Button
            type="link"
            icon={<LinkOutlined />}
            href={course.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ padding: 0, marginTop: 12 }}
          >
            访问课程
          </Button>
        </div>
      </Card>
    );
  };

  // 书籍卡片
  const BookCard: React.FC<{ book: Book }> = ({ book }) => (
    <Card 
      hoverable 
      style={{ height: '100%' }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ marginBottom: 8, fontSize: 16 }}>{book.title}</h3>
          <p style={{ color: '#666', fontSize: 14, marginBottom: 8 }}>
            作者：{book.author}
          </p>
          {book.publisher && (
            <p style={{ color: '#999', fontSize: 13, marginBottom: 8 }}>
              出版社：{book.publisher}
            </p>
          )}
          {book.rating && book.rating !== '待评分' && (
            <div style={{ marginBottom: 12 }}>
              <Rate disabled defaultValue={Number(book.rating) || 0} style={{ fontSize: 14 }} />
              <span style={{ marginLeft: 8, color: '#666' }}>{book.rating}</span>
            </div>
          )}
          {book.level && (
            <Tag color={
              book.level === 'beginner' ? 'green' :
              book.level === 'intermediate' ? 'blue' : 'red'
            }>
              {book.level === 'beginner' ? '入门' :
               book.level === 'intermediate' ? '进阶' : '高级'}
            </Tag>
          )}
          <p style={{ marginTop: 12, fontSize: 13, color: '#666', lineHeight: 1.6, maxHeight: 60, overflow: 'hidden' }}>
            {book.description}
          </p>
        </div>
        <Button
          type="link"
          icon={<LinkOutlined />}
          href={book.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ padding: 0, marginTop: 12 }}
        >
          查看详情
        </Button>
      </div>
    </Card>
  );

  // 证书卡片
  const CertCard: React.FC<{ cert: Certification }> = ({ cert }) => (
    <Card 
      hoverable 
      style={{ height: '100%' }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ marginBottom: 8, fontSize: 16 }}>{cert.title}</h3>
          <p style={{ color: '#666', fontSize: 14, marginBottom: 8 }}>
            认证机构：{cert.provider || cert.issuer}
          </p>
          {cert.validity && (
            <p style={{ color: '#999', fontSize: 13, marginBottom: 8 }}>
              有效期：{cert.validity}
            </p>
          )}
          {cert.rating && typeof cert.rating === 'number' && (
            <div style={{ marginBottom: 12 }}>
              <Rate disabled defaultValue={cert.rating} style={{ fontSize: 14 }} />
              <span style={{ marginLeft: 8, color: '#666' }}>{cert.rating}</span>
            </div>
          )}
          {cert.level && (
            <Tag color={
              cert.level === 'beginner' || cert.level === '入门级' ? 'green' :
              cert.level === 'intermediate' || cert.level === '专业级' ? 'blue' : 'red'
            }>
              {cert.level === 'beginner' ? '入门级' :
               cert.level === 'intermediate' ? '专业级' : 
               cert.level === 'advanced' ? '专家级' : cert.level}
            </Tag>
          )}
          <p style={{ marginTop: 12, fontSize: 13, color: '#666', lineHeight: 1.6, maxHeight: 60, overflow: 'hidden' }}>
            {cert.description}
          </p>
        </div>
        <Button
          type="link"
          icon={<LinkOutlined />}
          href={cert.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ padding: 0, marginTop: 12 }}
        >
          了解认证
        </Button>
      </div>
    </Card>
  );

  // 课程列表
  const CoursesGrid = () => {
    if (!courses || courses.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <Empty
            image={<ReadOutlined style={{ fontSize: 48, color: '#1677ff' }} />}
            description="课程推荐尚未生成"
          >
            <GenerateContentButton
              pathId={pathId}
              contentType="courses"
              onGenerated={onCoursesGenerated}
            />
          </Empty>
        </div>
      );
    }

    return (
      <>
        <Row gutter={[16, 16]}>
          {courses.map((course, index) => (
            <Col xs={24} sm={12} md={8} key={`${course.url}-${index}`}>
              <CourseCard course={course} />
            </Col>
          ))}
        </Row>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <GenerateContentButton
            pathId={pathId}
            contentType="courses"
            onGenerated={onCoursesGenerated}
            buttonText="生成更多课程推荐"
            icon={<PlusOutlined />}
          />
        </div>
      </>
    );
  };

  // 书籍列表
  const BooksGrid = () => {
    if (!books || books.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <Empty
            image={<BookOutlined style={{ fontSize: 48, color: '#1677ff' }} />}
            description="书籍推荐尚未生成"
          >
            <GenerateContentButton
              pathId={pathId}
              contentType="books"
              onGenerated={onBooksGenerated}
            />
          </Empty>
        </div>
      );
    }

    return (
      <>
        <Row gutter={[16, 16]}>
          {books.map((book, index) => (
            <Col xs={24} sm={12} md={8} key={`${book.url}-${index}`}>
              <BookCard book={book} />
            </Col>
          ))}
        </Row>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <GenerateContentButton
            pathId={pathId}
            contentType="books"
            onGenerated={onBooksGenerated}
            buttonText="生成更多书籍推荐"
            icon={<PlusOutlined />}
          />
        </div>
      </>
    );
  };

  // 证书列表
  const CertificationsGrid = () => {
    if (!certifications || certifications.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <Empty
            image={<TrophyOutlined style={{ fontSize: 48, color: '#1677ff' }} />}
            description="证书推荐尚未生成"
          >
            <GenerateContentButton
              pathId={pathId}
              contentType="certifications"
              onGenerated={onCertificationsGenerated}
            />
          </Empty>
        </div>
      );
    }

    return (
      <>
        <Row gutter={[16, 16]}>
          {certifications.map((cert, index) => (
            <Col xs={24} sm={12} md={8} key={`${cert.url}-${index}`}>
              <CertCard cert={cert} />
            </Col>
          ))}
        </Row>
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <GenerateContentButton
            pathId={pathId}
            contentType="certifications"
            onGenerated={onCertificationsGenerated}
            buttonText="生成更多证书推荐"
            icon={<PlusOutlined />}
          />
        </div>
      </>
    );
  };

  return (
    <Tabs
      activeKey={activeKey}
      onChange={setActiveKey}
      items={[
        {
          key: 'courses',
          label: (
            <span>
              <ReadOutlined />
              推荐课程
            </span>
          ),
          children: <CoursesGrid />
        },
        {
          key: 'books',
          label: (
            <span>
              <BookOutlined />
              推荐书籍
            </span>
          ),
          children: <BooksGrid />
        },
        {
          key: 'certifications',
          label: (
            <span>
              <TrophyOutlined />
              职业证书
            </span>
          ),
          children: <CertificationsGrid />
        }
      ]}
    />
  );
};

export default ResourcesTab;

