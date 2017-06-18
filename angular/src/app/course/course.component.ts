import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router'
import { ServerService } from '../service/server.service'

@Component({
  selector: 'app-course',
  templateUrl: './course.component.html',
  styleUrls: ['./course.component.scss']
})
export class CourseComponent implements OnInit {

  id: number;
  type: string;
  name: string;
  modules: [any];
  solved: [number];
  completed: boolean = true;
  loading = true;


  constructor(private route: ActivatedRoute, private server: ServerService) {

  }

  ngOnInit(){
    this.route.params.subscribe(data => {
      this.id = data.id
      this.load();
    })
  }

  load() {

    this.server.get('courses/'+this.id + "/", true)
      .then(data => {
        this.name = data.name;
        this.modules = data.modules;
        this.solved = data.solved;

        let lastModule = this.modules[this.modules.length - 1]
        let lastQuestion = lastModule.question[lastModule.question.length - 1]
        if(!(data.solved.indexOf(lastQuestion.id) > -1)){
          this.completed = false;
        }
        this.loading = false
      })
  }



}
